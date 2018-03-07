import os.path as path
import logging
import yaml
from django.core.management.base import BaseCommand

from newsarticles.scrapers import scrape_articles

LOG = logging.getLogger(__name__)

SCRAPER_CONFIG = '../../conf/scrapers.yaml'
CONFIG_PATH = path.abspath(path.join(path.dirname(__file__), SCRAPER_CONFIG))


class Command(BaseCommand):
    help = "Run the news article scrapers, writing to the database"

    def add_arguments(self, parser):
        parser.add_argument('scraper', nargs='?')

    def handle(self, *args, **options):
        cfg_file = open(CONFIG_PATH, 'r')
        all_scrapers = yaml.load(cfg_file)

        if options['scraper']:
            scraper_name = options['scraper']
            LOG.info('Running scrapers for news source %s', scraper_name)

            matched_scrapers = [scraper for scraper in all_scrapers
                                if scraper.get('news_source') == scraper_name]
        else:
            matched_scrapers = all_scrapers
            LOG.info('Running all scrapers')

        if not len(matched_scrapers):
            LOG.critical('No matching scrapers found')
            return

        scrape_articles(matched_scrapers)
