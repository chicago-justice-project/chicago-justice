from django.contrib.gis.db import models as gismodels
from django.db import models

from newsarticles.basescraper import BaseScraper

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

class NewsSource(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256)
    legacy_feed_id = models.CharField(max_length=8, blank=True, db_index=True)

    def __unicode__(self):
        return self.name

# dict of int->scraper class
SCRAPER_TYPES = {
    0: BaseScraper,
}

SCRAPER_TYPE_CHOICES = [(k, v.__name__) for k, v in SCRAPER_TYPES.iteritems()]

class NewsScraper(models.Model):
    short_name = models.CharField(max_length=256)
    news_source = models.ForeignKey(NewsSource)
    enabled = models.BooleanField(default=True)
    scraper_type = models.PositiveSmallIntegerField(choices=SCRAPER_TYPE_CHOICES)

    # JSON serialized config for scraper
    config = models.TextField()


class Category(models.Model):
    category_name = models.CharField(max_length=256)
    abbreviation = models.CharField(max_length=5)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.category_name, self.abbreviation)

    class Meta:
        ordering = ['abbreviation']

class Article(models.Model):
    news_source = models.ForeignKey(NewsSource, null=True, db_index=True)
    url = models.CharField(max_length=1024, unique=True, db_index=True)
    orig_html = models.TextField()
    title = models.TextField()
    bodytext = models.TextField()
    relevant = models.BooleanField(db_index=True)
    categories = models.ManyToManyField(Category)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    objects = gismodels.GeoManager()

    # Deprecated, use news_source instead.
    feedname = models.CharField(max_length=1, editable=False, db_index=True)

