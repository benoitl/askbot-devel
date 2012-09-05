import sys
from django.core.management.base import BaseCommand, CommandError
from askbot import const
from askbot import models
import os
from askbot.utils import mail

class Command(BaseCommand):
    args = '<message file>'
    help = 'Send a broadcast email to all users'
             
    def handle(self, *args, **options):
        if len(args) != 1:
          print "Need a message file"
          return

        if not os.path.exists(args[0]):
           print "File '%s' does not exist" % args[0]
           return

        message=open(args[0], 'r').read()
        title = message.split('\n')[0]
        print "Title: ", title
        print "Message:\n", message

        users = models.User.objects.all().order_by('username')
        for user in users:
          if len(user.email) > 5:
              mail.send_mail(
                  subject_line = title,
                  body_text = message,
                  recipient_list = [user.email]
              ) 
                                                                           
