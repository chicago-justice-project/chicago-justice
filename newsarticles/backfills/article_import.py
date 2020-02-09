import os.path as path
import logging
import datetime
import yaml
import csv

from newsarticles.scrapers.article import ArticleScraper, ArticleResult
from newsarticles.tagging import tag_article

"""
The following is meant to parse a CSV file of articles that need to be imported
because, e.g., the scrapers went down for a while. This file is expected to
have at least three columns with a header row that has the news source
abbreviation (it must match what is in the YAML config file for the scrapers),
the date of the article, and the link to the article. The header row labels and
date format should match or be specified using the global variables set below.
The encoding of the CSV file is assumed to be utf-8-sig in order to remove any
BOM present in the file.
"""

LOG = logging.getLogger(__name__)

SCRAPER_CONFIG = '../conf/scrapers.yaml'
CONFIG_PATH = path.abspath(path.join(path.dirname(__file__), SCRAPER_CONFIG))
SOURCE_HEADER = 'News Source Abbreviation'
LINK_HEADER = 'Article Link'
DATE_HEADER = 'Date'
DATE_FORMAT = '%m/%d/%y'
TIME = datetime.datetime.now().time()

def run(csv_file):
    processed = 0
    skipped = 0
    errored = 0
    cfg_file = open(CONFIG_PATH, 'r')
    all_scrapers = yaml.load(cfg_file)
    file = open(csv_file, newline='', encoding='utf-8-sig')
    reader = csv.DictReader(file)
    try:
        for row in reader:
            news_source = row[SOURCE_HEADER]
            url = row[LINK_HEADER]
            date = row[DATE_HEADER]
            dt = datetime.datetime.combine(datetime.datetime.strptime(date, DATE_FORMAT), TIME)
            for scraper in all_scrapers:
                if scraper.get('news_source') == news_source:
                    matched_scraper = scraper
                    break
                else:
                    matched_scraper = False
            if matched_scraper:
                LOG.info('Scraping article from {} with url: {}'.format(matched_scraper['news_source'], url))
                response = scrape(matched_scraper, url, dt)
                if response == 'success':
                    processed += 1
                elif response == 'skip':
                    skipped += 1
                elif response == 'error':
                    errored += 1
            else:
                LOG.warn('Could not find %s in scraper config file', news_source)
                errored += errored
    except csv.Error as e:
        LOG.warn('Error reading file {}, at line {}: {}'.format(csv_file, reader.line_num, e))
    LOG.info('Imported: {}\tSkipped: {}\tErrors: {}'.format(processed, skipped, errored))

def scrape(scraper_cfg, url, dt):
    scraper = ArticleScraper(config=scraper_cfg)
    try:
        result = scraper.process_link(url, True)
        if result.article and result.success and result.status == ArticleResult.CREATED:
            try:
                result.article.save()
                result.article.created = dt # Have to wait to update created time until Article object created first
                result.article.save()
                tag_article(result.article)
                return 'success'
            except:
                LOG.warn('Cannot save scraped article to database')
        elif result.status == ArticleResult.SKIPPED or result.status == ArticleResult.EXISTS:
            LOG.info('Article already exists with url: {}'.format(url))
            return 'skip'
        elif result.status == ArticleResult.ERROR:
            LOG.warn('Error parsing url: {}'.format(url))
            return 'error'
    except:
        LOG.warn('Unable to scrape the link: {}'.format(url))
        return 'error'
