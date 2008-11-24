import logging
from django.core.management.base import NoArgsCommand
from mailer.engine import send_all
from milestone.cron import run_milestone_cron

class Command(NoArgsCommand):
    help = 'Run the rancho Cron'
    
    def handle_noargs(self, **options):
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
        print "Milestone's cron..."
        run_milestone_cron()  
