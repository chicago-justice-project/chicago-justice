# Collect all scraper modules

from datetime import datetime, timedelta
from newsarticles.models import Article

import abclocalScraper
import beachwoodScraper
import betterGovScraper
import cbslocalScraper
import chicagoMagazineScraper
import chicagoNowScraper
import chicagoReaderScraper
import chicagoReporterScraper
import crainsScraper
import dailyHeraldScraper
import defenderScraper
import dnaInfoScraper
import foxchicagoScraper
import nbclocalScraper
import suntimesScraper
import tribuneScraper
import wbezScraper
import wgntvScraper
import windyCityTimesScraper
import wlsScraper
import wttwScraper

all_scrapers = (
    abclocalScraper,
    beachwoodScraper,
    betterGovScraper,
    cbslocalScraper,
    chicagoMagazineScraper,
    chicagoNowScraper,
    chicagoReaderScraper,
    chicagoReporterScraper,
    crainsScraper,
    dailyHeraldScraper,
    defenderScraper,
    dnaInfoScraper,
    foxchicagoScraper,
    nbclocalScraper,
    suntimesScraper,
    tribuneScraper,
    wbezScraper,
    wgntvScraper,
    windyCityTimesScraper,
    wlsScraper,
    wttwScraper,
)

def run_scraper(scraper_name):
    name = scraper_name.lower()
    for s in all_scrapers:
        if (name in s.__name__.lower()):
            run_scraper_module(s)
            return
    raise Exception("No scraper named %s" % scraper_name)


def run_all():
    for s in all_scrapers:
        run_scraper_module(s)

    cleanup_old_articles()


def cleanup_old_articles():
    """ remove original HTML for articles older than two weeks """
    now = datetime.now()
    keepdate = now - timedelta(days=14)
    old_articles = Article.objects.filter(created__lte=keepdate).exclude(orig_html='').iterator()
    for article in old_articles:
        article.orig_html = ''
        article.save()

    # clean up the tables
    for table in (Article, ):
        table.objects.raw('VACUUM %s' % table._meta.db_table)

def run_scraper_module(scraper_module):
    # don't crash on any errors in a single scraper
    # hopefully we will catch in in the logs
    try:
        scraper_module.main()
    except Exception as e:
        print("ERROR: Feed crashed: %s" % scraper_module.__name__)
        print("ERROR: Reason %s" % e)


foo = 'ha'

#import pkgutil
#import inspect
#
#for loader, name, is_pkg in pkgutil.walk_packages(__path__):
#    module = loader.find_module(name).load_module(name)
#
#    for name, value in inspect.getmembers(module):
#        if name.startswith('__'):
#            continue
#        print(name)
#
#        globals()[name] = value
#        __all__.append(name)
