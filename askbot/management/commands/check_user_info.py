"""management command that renames a tag or merges
it to another, all corresponding questions are automatically
retagged
"""
import sys
from optparse import make_option
from django.core import management
from django.core.management.base import BaseCommand, CommandError
from askbot import api, models
from askbot.utils import console
from askbot.deps.django_authopenid.ldap_auth import ldap_authenticate
import askbot.deps.django_authopenid.util as util


class Command(BaseCommand):
    "The command object itself"

    help = """Get the user information
    """
    option_list = BaseCommand.option_list + (
        make_option('--user',
            action = 'store',
            type = 'str',
            dest = 'user',
            default = None,
            help = 'username to check'
        ),
        make_option('--pass',
            action = 'store',
            type = 'str',
            dest = 'pass',
            default = None,
            help = 'username to check'
        ),
    )

    def handle(self, *args, **options):
        """command handle function. 
        """
        if options['user'] is None:
            raise CommandError('the --user argument is required')
        user = options['user']
        pw = options['pass']
        if pw is None:
          pw = "dummy"

        result = util.ldap_check_password(user, pw)
        print result

