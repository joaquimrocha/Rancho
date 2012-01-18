from django.core.management.base import NoArgsCommand
from rancho.milestone.cron import run_milestone_cron
import logging

class Command(NoArgsCommand):
    help = 'Run the rancho Cron'

    def handle_noargs(self, **options):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        try:
            run_milestone_cron()
        except Exception, inst:
            print "milestone problem", inst

        try:
            from rancho.mailer.management.commands.retry_deferred import Command as C_retry_deferred
            from rancho.mailer.management.commands.send_mail import Command as C_send_mail
            C_retry_deferred().handle_noargs()
            C_send_mail().handle_noargs()
        except Exception, inst:
            print "send mail problems", inst
