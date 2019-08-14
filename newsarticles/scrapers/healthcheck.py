import logging
import datetime

from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import NewsSource, ScraperResult

LOG = logging.getLogger(__name__)

def run(min_fails):
    news_sources = NewsSource.objects.all()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    for news_source in news_sources:
        try:
            failure = ScraperResult.objects.filter(news_source=news_source, success=False, completed_time__gt=yesterday).count()
        except ObjectDoesNotExist:
            failure = True
        print('The source %s has failed %d times' %(news_source.name, failure))
