import os

from newsarticles.scrapers import (
    abclocalScraper,
    beachwoodScraper,
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

scrapers = (chicagoReporterScraper,
            windyCityTimesScraper, wlsScraper, dnaInfoScraper,
            chicagoReaderScraper, crainsScraper,
            chicagoMagazineScraper, defenderScraper, chicagoNowScraper,
            wttwScraper, cbslocalScraper, wbezScraper, nbclocalScraper,
            abclocalScraper, wgntvScraper, beachwoodScraper,
            tribuneScraper, suntimesScraper, foxchicagoScraper,
            dailyHeraldScraper,
            )

from newsarticles.models import Article
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Run the news article scrapers, writing to the database"

    def handle(self, *args, **options):
        # download data
        for s in scrapers:
            # don't crash on any errors in a single scraper
            # hopefully we will catch in in the logs
            try:
                s.main()
            except Exception as e:
                self.stdout.write("ERROR: Feed crashed: %s" % s)
                self.stdout.write("ERROR: Reason %s" % e)

        # remove original HTML for articles older than two weeks
        now = datetime.now()
        keepdate = now - timedelta(days=14)
        old_articles = Article.objects.filter(created__lte=keepdate).exclude(orig_html='').iterator()
        for article in old_articles:
            article.orig_html = ''
            article.save()

        # clean up the tables
        for table in (Article, ):
            table.objects.raw('VACUUM %s' % table._meta.db_table)
