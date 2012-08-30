"""put this file into your askbot/management/commands
directory"""
from django.core.management.base import NoArgsCommand
from askbot import models
from askbot.utils.console import ProgressBar

class Command(NoArgsCommand):
    """Migrates marked tags from Windriver format
    to AskBot's
    usage: python manage.py wr_migrate_marked_tags
    """
    def handle_noargs(self, **options):
        marks = models.MarkedTag.objects.all()
        msg = 'Migrating marked tags:'
        for mark in ProgressBar(marks, marks.count(), message = msg):
            reason = mark.reason

            if set(reason) != set('SFI'):
                continue

            if 'S' in reason:
                if len(reason) > 1:
                    new_mark = models.MarkedTag()
                    new_mark.tag = mark.tag
                    new_mark.user = mark.user
                    new_mark.reason = 'subscribed'
                    new_mark.save()
                    reason = reason.replace('S', '')
                else:
                    mark.reason = 'subscribed'
                    mark.save()
                    continue

            if reason == '':
                continue

            assert(len(reason) < 3)

            if set(reason) == set('FI'):
                mark.reason = 'good'
                mark.save()
            elif reason == 'I':
                mark.reason = 'bad'
            else:
                assert(reason == 'F')
                mark.reason = 'good'

            mark.save()
