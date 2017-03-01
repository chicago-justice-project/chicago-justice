# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


FEED_ABCLOCAL         = 'A'
FEED_NBCLOCAL         = 'B'
FEED_BEACHWOOD        = 'C'
FEED_DEFENDER         = 'D'
FEED_CHICAGOREADER    = 'E'
FEED_FOX              = 'F'
FEED_WGNTV            = 'G'
FEED_DNAINFO          = 'I'
FEED_CHICAGOJOURNAL   = 'J'
FEED_CBSLOCAL         = 'L'
FEED_CHICAGOMAGAZINE  = 'M'
FEED_NEWSCOOP         = 'N'
FEED_CHICAGONOW       = 'O'
FEED_CRAINS           = 'R'
FEED_SUNTIMES         = 'S'
FEED_TRIBUNE          = 'T'
FEED_WLSAM            = 'U'
FEED_WINDYCITYTIMES   = 'V'
FEED_WTTW             = 'W'
FEED_CHICAGOREPORTER  = 'X'
FEED_WBEZ             = 'Z'
FEED_DAILYHERALD      = 'a'     # TODO: change feed ID to more than one char
FEED_BETTERGOV        = 'b'
FEED_NAMES = (
    (FEED_ABCLOCAL       , 'ABC Local'),
    (FEED_BEACHWOOD      , 'Beachwood Reporter'),
    (FEED_CBSLOCAL       , 'CBS Local'),
    (FEED_DEFENDER       , 'Chicago Defender'),
    (FEED_CHICAGOMAGAZINE, 'Chicago Magazine'),
    (FEED_CHICAGOJOURNAL , 'Chicago Journal'),
    (FEED_CHICAGONOW     , 'Chicago Now'),
    (FEED_CHICAGOREADER  , 'Chicago Reader'),
    (FEED_CHICAGOREPORTER, 'Chicago Reporter'),
    (FEED_CRAINS         , 'Crains'),
    (FEED_DNAINFO        , 'DNAInfo Chicago'),
    (FEED_FOX            , 'Fox Chicago'),
    (FEED_NBCLOCAL       , 'NBC Local'),
    (FEED_NEWSCOOP       , 'Chicago News Cooperative'),
    (FEED_SUNTIMES       , 'Chicago Sun-Times'),
    (FEED_TRIBUNE        , 'Chicago Tribune'),
    (FEED_WBEZ           , 'WBEZ'),
    (FEED_WGNTV          , 'WGN TV'),
    (FEED_WINDYCITYTIMES , 'Windy City Times'),
    (FEED_WLSAM          , 'WLS AM'),
    (FEED_WTTW           , 'WTTW'),
    (FEED_DAILYHERALD    , 'Daily Herald'),
    (FEED_BETTERGOV      , 'Better Government Association'),
)


def populate_news_sources(apps, schema_editor):
    NewsSource = apps.get_model('newsarticles', 'NewsSource')

    for (char_id, name) in FEED_NAMES:
        short_name = name.lower().replace(' ', '-')
        ns = NewsSource(name=name, short_name=short_name, legacy_feed_id=char_id)
        ns.save()

def populate_articles(apps, schema_editor):
    Article = apps.get_model('newsarticles', 'Article')
    NewsSource = apps.get_model('newsarticles', 'NewsSource')

    # Cache sources
    sources = {}
    for ns in NewsSource.objects.all():
        sources[ns.legacy_feed_id] = ns

    for article in Article.objects.all():
        article.news_source = sources[article.feedname]
        article.save(update_fields=['news_source'])


class Migration(migrations.Migration):

    dependencies = [
        ('newsarticles', '0002_add_news_source_model'),
    ]

    operations = [
        migrations.RunPython(populate_news_sources),
        migrations.RunPython(populate_articles),
    ]
