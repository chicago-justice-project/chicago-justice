from newsarticles.scrapers import cpdScraper

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Run CPD scraper"

    def add_arguments(self, parser):
        parser.add_argument('--rebuild', action='store_true', dest='rebuild', default=False)

    def handle(self, *args, **options):
        cpdScraper.main(options['rebuild'])
