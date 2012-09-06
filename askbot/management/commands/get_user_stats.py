import sys
import optparse
import datetime
from django.core.management.base import BaseCommand, CommandError
from askbot import models
from django.conf import settings as django_settings

base_report_dir = django_settings.REPORT_BASE


def format_table_row(*cols, **kwargs):
        bits = list()
        for col in cols:
            bits.append(col)
        line = kwargs['format_string'] % tuple(bits)

        return line


class Command(BaseCommand):
    help = """Dump user reputation statistics."""

    option_list = BaseCommand.option_list + (
        optparse.make_option('--file',
            action = 'store_true',
            dest = 'save_file',
            default = False,
            help = 'Save results to file.'
        ),
    )
     
    def handle(self, *args, **options):
        out = 'User Stats for %s\n' % datetime.date.today()
        out += self.print_user_sub_counts()

        if options['save_file'] == True:
           fd = open("%s/%s" % (base_report_dir, 'user_stats.txt') , 'w')
           fd.write(out.encode("iso-8859-15", "replace"))
           fd.close()
        else:
           print out


    def print_user_sub_counts(self):
        """prints list of users and their stats
        """
        users = models.User.objects.all().order_by('username')
        item_count = 0
        out = '%-25s %4s %6s %6s %6s %6s %6s %6s %6s\n' % (
       'User', 'id', '# Q', '# A', 'Votes', 'Karma','Gold','Silver','Bronze')
        out +='%-25s %4s %6s %6s %6s %6s %6s %6s %6s\n' % (
        '=========================', '====', '===', '===', '=====', '=====', '====', '======', '======')
        for user in users:
            user_string = '%-25s %4s' % (user.username, user.id)
            line = format_table_row(
                                user_string, user.posts.get_questions().count(), user.posts.get_answers().count(),
                                models.Vote.objects.get_up_vote_count_from_user(user) + 
                                models.Vote.objects.get_down_vote_count_from_user(user),
                                user.reputation, user.gold, user.silver, user.bronze,
                                format_string = '%-30s %6s %6s %6s %6s %6s %6s %6s'
                            )
            out +=line + '\n'

        return out
