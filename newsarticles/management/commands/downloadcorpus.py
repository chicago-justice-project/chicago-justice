import os.path as path
import logging
import nltk
from django.core.management.base import BaseCommand

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Download NLTK corpus data"

    def handle(self, *args, **options):
        LOG.info('Downloading NLTK data')
        nltk.download('punkt')
        nltk.download('wordnet')
