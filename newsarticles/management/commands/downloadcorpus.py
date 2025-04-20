import os.path as path
import logging
import nltk
from django.core.management.base import BaseCommand

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download NLTK corpus data"

    def add_arguments(self, parser):
        parser.add_argument('download_dir', nargs='?')

    def handle(self, *args, **options):
        LOG.info('Downloading NLTK data')

        if options['download_dir']:
            dest = options['download_dir']
            nltk.download('punkt_tab', download_dir=dest)
            nltk.download('wordnet', download_dir=dest)
        else:
            nltk.download('punkt_tab')
            nltk.download('wordnet')
