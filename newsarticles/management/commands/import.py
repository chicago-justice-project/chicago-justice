import os.path as path
import logging
from django.core.management.base import BaseCommand

from newsarticles.backfills import article_import

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Import collection of articles from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='?', help='Path to CSV file to be processed')

    def handle(self, *args, **options):
        file = options['csv_file']
        file = path.abspath(path.expanduser(path.expandvars(file)))
        LOG.info('Processing {} for articles'.format(file))
        article_import.run(file)
