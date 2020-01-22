import logging
from django.core.management.base import BaseCommand

from newsarticles.scrapers import sentiment

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run sentiment analysis on articles"

    def handle(self, *args, **options):
        LOG.info('Running backfill on outdated articles')
        sentiment.run()
