import sys
import optparse
import datetime
from django.core.management.base import BaseCommand, CommandError
from askbot import models
from django.conf import settings as django_settings
import askbot.deps.django_authopenid.util as util
import string


base_report_dir = django_settings.REPORT_BASE


def format_table_row(*cols, **kwargs):
        bits = list()
        for col in cols:
            bits.append(col)
        line = kwargs['format_string'] % tuple(bits)

        return line


class Command(BaseCommand):
    help = """Validate User Records and Fix problems."""

    option_list = BaseCommand.option_list + (
        optparse.make_option('--fix',
            action = 'store_true',
            dest = 'fix',
            default = False,
            help = 'fix issues'
        ),
        optparse.make_option('--file',
            action = 'store_true',
            dest = 'save_file',
            default = False,
            help = 'Save results to file.'
        ),
    )
     
    def handle(self, *args, **options):
        out = 'User Validation for %s\n' % datetime.date.today()
        out += self.print_user_validations(options['fix'])

        if options['save_file'] == True:
           fd = open("%s/%s" % (base_report_dir, 'user_stats.txt') , 'w')
           fd.write(out.encode("iso-8859-15", "replace"))
           fd.close()
        else:
           print out


    def print_user_validations(self, fix):
        """prints results of validation
        """
        users = models.User.objects.all().order_by('username')
        out = '%-25s %4s %15s %16s %26s\n' % (
       'User', 'id', 'First', 'Last', 'email')
        out +='%-25s %4s %15s %16s %26s\n' % (
        '=========================', '====', '=============', '==============', '=========================')
        problem_list = []
        for user in users:
            if (len(user.first_name) == 0 or len(user.last_name) == 0 or 
                len(user.email) == 0):
                problem_list.append(user)

        item_count = len(problem_list)
        for user in problem_list:
            result = util.ldap_check_password(user.username, "dummy")

            ln = ' '
            fn = ' '
            em = ' '
            if len(result['email']) == 0:
               out += '*' 
            else:
               if len(user.last_name) == 0:
                  user.last_name = result['last_name']
                  ln = '*'
               if len(user.first_name) == 0:
                  user.first_name = result['first_name']
                  fn = '*'
               if len(user.email) == 0:
                  user.email = result['email']
                  em = '*'
               if ln == '*' and fn == '*':
                  user.username = string.capitalize(user.first_name) + '.' + string.capitalize(user.last_name)
               if fix == True:
                  user.save()
               
            user_string = '%-25s %4s' % (user.username, user.id)
            line = format_table_row(
                                user_string, fn, user.first_name, 
                                ln, user.last_name, em, user.email,
                                format_string = '%-30s %1s%16s %1s%16s %1s%26s'
                            )
            out +=line + '\n'

        return out
