import logging
import datetime
import smtplib, ssl

from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import NewsSource, ScraperResult

LOG = logging.getLogger(__name__)

def run(min_fails):
    news_sources = NewsSource.objects.all()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    failed_scrapers = {} # dictionary to store failed scrapers
    for news_source in news_sources:
        try:
            failures = ScraperResult.objects.filter(news_source=news_source, success=False, completed_time__gt=yesterday).count()
        except ObjectDoesNotExist:
            LOG.warn('%s has no scraper results', news_source)
            failures = None
        if failures and failures >= min_fails:
            failed_scrapers[news_source] = failures

    for failure in failed_scrapers:
        print('The source %s has failed %d times in the last day.' %(failure, failed_scrapers[failure]))

    failed_scrapers.clear()
