#!/usr/bin/env python

import abclocalScraper
import beachwoodScraper
import cbslocalScraper
import chicagoMagazineScraper
import chicagoNowScraper
import chicagoJournalScraper
import chicagoReaderScraper
import chicagoReporterScraper
import crainsScraper
import defenderScraper
import dnaInfoScraper
import nbclocalScraper
import suntimesScraper
import tribuneScraper
import wbezScraper
import wgntvScraper
import windyCityTimesScraper
import wlsScraper
import wttwScraper

scrapers = (chicagoReporterScraper,
            windyCityTimesScraper, wlsScraper, dnaInfoScraper,
            chicagoReaderScraper, crainsScraper, chicagoJournalScraper,
            chicagoMagazineScraper, defenderScraper, chicagoNowScraper,
            wttwScraper, cbslocalScraper, wbezScraper, nbclocalScraper,
            abclocalScraper, wgntvScraper, beachwoodScraper,
            tribuneScraper, suntimesScraper, 
           )

from cjp.newsarticles.models import Article
from datetime import datetime, timedelta

# download data
for s in scrapers:
    # don't crash on any errors in a single scraper
    # hopefully we will catch in in the logs
    try:
        s.main()
    except Exception as e:
        print "ERROR: Feed crashed: %s" % s
        print "ERROR: Reason %s" % e

# remove original HTML for articles older than two weeks
#
# 5/13/2012 Reed's patch
# keeps Django from loading all records into memory.  
# Using an iterator now
#
now = datetime.now()
keepdate = now - timedelta(days=14)
old_articles = Article.objects.filter(created__lte = keepdate).exclude(orig_html = '').iterator()
for article in old_articles:
    article.orig_html = ''
    article.save()

# clean up the tables
for table in (Article, ):
    table.objects.raw('VACUUM %s' % table._meta.db_table)
