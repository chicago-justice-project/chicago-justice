import logging
from django.core.management.base import BaseCommand

from newsarticles.scrapers import healthcheck

LOG = logging.getLogger(__name__)

DEFAULT_MIN_FAILS = 5 # Number of times scraper can fail to trigger email

class Command(BaseCommand):
    help = "Run health check of scrapers"

    def add_arguments(self, parser):
        parser.add_argument('from_email', type=str, help='Email address from which the health check report should be sent')
        parser.add_argument('to_email', nargs='+', type=str, help='Email address(es) to which the healtch check report should sent (can be more than one)')

        parser.add_argument('--minfails', '-m', nargs='?', type=int, default=DEFAULT_MIN_FAILS, help='Number of times scraper can fail in 24-hours before being marked as a failed scraper')

    def handle(self, *args, **options):
        LOG.info('Running health check of scrapers')
        healthcheck.run(options['minfails'], options['from_email'], options['to_email'])
