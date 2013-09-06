import sys
import optparse
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
import os
import re


class Command(BaseCommand):
    help = 'Prints statistics of tag usage'

    option_list = BaseCommand.option_list + (
            optparse.make_option('--log',
                action = 'store',
                type = 'str',
                dest = 'log_file',
                default = None,
                help = 'Log file to parse.'
            ),
            optparse.make_option('--file',
                action = 'store',
                type = 'str',
                dest = 'save_file',
                default = None,
                help = 'Save results to file.'
            ),
        )
    def handle(self, *args, **options):
        if not(options['log_file']):
            raise CommandError('Please specify a log file with --log')

        if not os.path.isfile(options['log_file']):
            raise CommandError('Log file does not exist!')

        out='Mail Errors - %s\n\n' % datetime.today()
        fd = open("%s" % options['log_file'], "r")
        lines = fd.readlines()
        fd.close()
        mail_errors = []
        for line in lines:
           if 'User unknown' in line:
              mail_errors.append(line)

        users = extract_mail(mail_errors)
        out += '%d Users\n' % len(users)
        for u in users:
            out += '%s\n' % u

        if options['save_file']:
           fd = open("%s" % (fname) , 'w')
           fd.write(out.encode("iso-8859-15", "replace"))
           fd.close()
        else:
           print out
                                                                                       
u_re = re.compile("^.+'5.1.1 <([^>]+)>")
def extract_mail(lines):
  users = []
  for l in lines:
     m= u_re.match(l)
     if m:
        u = m.group(1)
        if not (u in users):
            users.append(u)

  return users
