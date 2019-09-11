import logging
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from newsarticles.models import NewsSource, ScraperResult

LOG = logging.getLogger(__name__)

def run(min_fails, from_email, to_email):
    news_sources = NewsSource.objects.all()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    failed_scrapers = {} # dictionary to store failed scrapers
    subject = 'CJP Scraper Healthcheck Status'
    message = "The following scraper(s) have failed more than {0} time(s) in the past 24 hours:\n".format(min_fails)

    for news_source in news_sources:
        try:
            failures = ScraperResult.objects.filter(news_source=news_source, success=False, completed_time__gt=yesterday).count()
        except ObjectDoesNotExist:
            LOG.warn('%s has no scraper results', news_source)
            failures = None
        if failures and failures >= min_fails:
            failed_scrapers[news_source] = failures

    message = message + '\n'.join('{0} failed {1} time(s)'.format(key, value) for key, value in failed_scrapers.items())

    if failed_scrapers:
        try:
            send_mail(subject, message, from_email, to_email)
            LOG.info('Email of failed scrapers sent')
        except:
            LOG.warn('Email of failed scrapers could not be sent')
    else:
        LOG.info('No failed scrapers found')

    failed_scrapers.clear()
