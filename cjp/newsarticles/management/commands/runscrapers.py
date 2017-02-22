from django.core.management.base import BaseCommand, CommandError

from newsarticles.scrapers import run_scraper, run_all
from newsarticles.models import Article

class Command(BaseCommand):
    help = "Run the news article scrapers, writing to the database"

    def add_arguments(self, parser):
        parser.add_argument('scraper', nargs='?')

    def handle(self, *args, **options):
        if (options['scraper']):
            print('Running scraper %s' % options['scraper'])
            run_scraper(options['scraper'])
        else:
            print('Running all scrapers')
            run_all()
