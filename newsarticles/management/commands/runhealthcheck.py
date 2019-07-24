import logging
from django.core.management.base import BaseCommand

from newsarticles.scrapers import healthcheck

LOG = logging.getLogger(__name__)

DEFAULT_MIN_FAILS = 5 # Number of times scraper can fail to trigger email

class Command(BaseCommand):
    help = "Run health check of scrapers"

    def add_arguments(self, parser):
        parser.add_argument('min_fails', nargs='?', type = int, default = DEFAULT_MIN_FAILS)

    def handle(self, *args, **options):
        LOG.info('Running health check of scrapers')
        healthcheck.run(options['min_fails'])
