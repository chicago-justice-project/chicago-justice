from __future__ import unicode_literals

from django.db import models
from django.contrib.gis.db import models as gismodels


class NewsSource(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256, db_index=True)
    legacy_feed_id = models.CharField(max_length=8, blank=True, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Category(models.Model):
    category_name = models.CharField(max_length=256)
    abbreviation = models.CharField(max_length=5)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return '{} ({})'.format(self.category_name, self.abbreviation)

    class Meta:
        ordering = ['abbreviation']


class ScraperResult(models.Model):
    news_source = models.ForeignKey(NewsSource, db_index=True)

    completed_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    added_count = models.PositiveSmallIntegerField(default=0)
    error_count = models.PositiveSmallIntegerField(default=0)
    total_count = models.PositiveSmallIntegerField(default=0)

    output = models.TextField(blank=True)

    def __unicode__(self):
        return '{} - {}'.format(self.news_source.name, self.completed_time)

class Article(models.Model):
    news_source = models.ForeignKey(NewsSource, null=True, db_index=True)
    url = models.CharField(max_length=1024, unique=True, db_index=True)
    title = models.TextField()
    author = models.CharField(max_length=1024, default="")
    bodytext = models.TextField()
    orig_html = models.TextField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    # Fields from classification/coding
    relevant = models.BooleanField(db_index=True)
    categories = models.ManyToManyField(Category)
    objects = gismodels.GeoManager()

    # Deprecated, use news_source instead.
    feedname = models.CharField(max_length=1, editable=False, db_index=True)

