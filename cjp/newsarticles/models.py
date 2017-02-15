from django.contrib.gis.db import models

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
)

class Category(models.Model):
    category_name = models.CharField(max_length=256)
    abbreviation = models.CharField(max_length=5)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.category_name, self.abbreviation)

    class Meta:
        ordering = ['abbreviation']

class Article(models.Model):
    feedname = models.CharField(max_length=1, choices=FEED_NAMES, db_index=True)
    url = models.CharField(max_length=1024, unique=True, db_index=True)
    orig_html = models.TextField()
    title = models.TextField()
    bodytext = models.TextField()
    relevant = models.BooleanField(db_index=True)
    categories = models.ManyToManyField(Category)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
    objects = models.GeoManager()


