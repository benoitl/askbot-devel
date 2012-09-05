"""management command that renames a tag or merges
it to another, all corresponding questions are automatically
retagged
"""
import sys
import datetime
from optparse import make_option
from django.core import management
from django.core.management.base import BaseCommand, CommandError
from askbot.deps.django_authopenid.models import UserAssociation
from askbot.deps.django_authopenid import util
from askbot import api, models
from askbot.utils import console


class Command(BaseCommand):
    "The command object itself"


    help = """Create a bogus user that can be used to deal with emails.

* if --user-id is provided, it will be used to set the user performing the operation
* The user must be either administrator or moderator
* if --user-id is not given, the earliest active site administrator will be assigned

    """
    option_list = BaseCommand.option_list + (
        make_option('--first',
            action = 'store',
            type = 'str',
            dest = 'first',
            default = None,
            help = 'First Name'
        ),
        make_option('--last',
            action = 'store',
            type = 'str',
            dest = 'last',
            default = None,
            help = 'Last Name'
        ),
        make_option('--username',
            action = 'store',
            type = 'str',
            dest = 'username',
            default = None,
            help = 'username'
        ),
        make_option('--email',
            action = 'store',
            type = 'str',
            dest = 'email',
            default = None,
            help = 'Email Address'
        ),
    )

    #@transaction.commit_manually
    def handle(self, *args, **options):
        """command handle function. reads tag names, decodes
        them using the standard input encoding and attempts to find
        the matching tags
        """
        if options['username'] is None:
            raise CommandError('the --username argument is required')
        if options['first'] is None:
            raise CommandError('the --first argument is required')
        if options['last'] is None:
            raise CommandError('the --last argument is required')
        if options['email'] is None:
            raise CommandError('the --email argument is required')

        username = options['username'].lower()
        user = util.setup_new_user(username, options['first'], options['last'],options['email'])
        assoc = UserAssociation(openid_url = username, user=user, provider_name = "Wind River LDAP")
        assoc.last_used_timestamp = datetime.datetime.now()
        assoc.save()
        print "Added User %s - %s %s - %s" % (username, options['first'], options['last'],
                options['email'])
