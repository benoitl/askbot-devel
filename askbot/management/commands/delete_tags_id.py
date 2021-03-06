"""management command that transfer tag usage data from
one tag to another and deletes the "from" tag

both "from" and "to" tags are identified by id

also, corresponding questions are retagged
"""
import re
import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from askbot import const, models
from askbot.utils import console
from askbot.management.commands.rename_tags import get_admin

def get_tags_by_ids(tag_ids):
    tags = list()
    for tag_id in tag_ids:
        try:
            tags.append(models.Tag.objects.get(id = tag_id))
        except models.Tag.DoesNotExist:
            raise CommandError('tag with id=%s not found' % tag_id)
    return tags

def get_similar_tags_from_strings(tag_strings, tag_name):
    """returns a list of tags, similar to tag_name from a set of questions"""

    grab_pattern = r'\b([%(ch)s]*%(nm)s[%(ch)s]*)\b' % \
                {'ch': const.TAG_CHARS, 'nm': tag_name}
    grab_re = re.compile(grab_pattern, re.IGNORECASE)

    similar_tags = set()
    for tag_string in tag_strings:
        similar_tags.update(
            grab_re.findall(tag_string)
        )
    return similar_tags

def parse_tag_ids(input):
    input = input.strip().split(' ')
    return set([int(i) for i in input])

def get_tag_names(tag_list):
    return set([tag.name for tag in tag_list])

def format_tag_name_list(tag_list):
    name_list = get_tag_names(tag_list)
    return u', '.join(name_list)

class Command(BaseCommand):
    "The command object itself"

    help = """remove tags from questions (as long as it's not the only one).
Like delete_tags, but using tag id's


"""
    option_list = BaseCommand.option_list + (
        make_option('--tags',
            action = 'store',
            type = 'str',
            dest = 'tags',
            default = None,
            help = 'list of tag IDs which needs to be removed'
        ),
        make_option('--user-id',
            action = 'store',
            type = 'int',
            dest = 'user_id',
            default = None,
            help = 'id of the user who will be marked as a performer of this operation'
        ),
    )

    #@transaction.commit_manually
    def handle(self, *args, **options):
        """command handle function. retrieves tags by id
        """
        try:
            tag_ids = parse_tag_ids(options['tags'])
        except:
            raise CommandError('Tag IDs must be integer')

        from_tags = get_tags_by_ids(tag_ids)
        admin = get_admin(options['user_id'])

        question_list = models.Thread.objects.all()
        for from_tag in from_tags:
            questions = question_list.filter(tags=from_tag)


            #print some feedback here and give a chance to bail out
            question_count = questions.count()
            if question_count == 0:
                print """Did not find any matching questions."""
                from_tag.delete()
                sys.stdout.write('Erased Tag %s\n' % from_tag.name)
                continue
            elif question_count == 1:
                print "One question matches:"
            elif question_count <= 10:
                print "%d questions match:" % question_count
            if question_count > 10:
                print "%d questions match." % question_count
                print "First 10 are:"
            for question in questions[:10]:
                print '* %s' % question.title.strip()


            prompt = 'Remove tags %s ?' % (from_tag.name)
            choice = console.choice_dialog(prompt, choices=('yes', 'no'))
            if choice == 'no':
                print 'Canceled'
                continue
            else:
                sys.stdout.write('Processing:')

            #actual processing stage, only after this point we start to
            #modify stuff in the database, one question per transaction
            from_tag_names = get_tag_names([from_tag])
            i = 0
            skip = 0
            for question in questions:
                tag_names = set(question.get_tag_names())
                orig = "%s" % tag_names
                # If it's the only tag, keep it
                if len(tag_names) == 1:
                    skip += 1
                    continue

                tag_names.difference_update(from_tag_names)

                print "%s -> %s" % (orig, tag_names)
                admin.retag_question(
                    question = question._question_post(),
                    tags = u' '.join(tag_names),
                    #silent = True #do we want to timestamp activity on question
                  )
                i += 1
                sys.stdout.write('%6.2f%%' % (100*float(i)/float(question_count)))
                sys.stdout.write('\b'*7)
                sys.stdout.flush()

            sys.stdout.write('\n')
            #transaction.commit()
            if skip < 1:
              # delete Tag from database
              #from_tag.delete()
              sys.stdout.write('Erased Tag %s\n' % from_tag_names)
            else:
                sys.stdout.write('Skipped %d Questions\n' % skip)
        # foreach tag ids
        #transaction.commit()
