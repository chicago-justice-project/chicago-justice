from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


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
    """
    A single run of a scraper.
    """
    news_source = models.ForeignKey(NewsSource, db_index=True)

    completed_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    added_count = models.PositiveSmallIntegerField(default=0)
    error_count = models.PositiveSmallIntegerField(default=0)
    total_count = models.PositiveSmallIntegerField(default=0)

    output = models.TextField(blank=True)

    def __unicode__(self):
        return '{} - {}'.format(self.news_source.name, self.completed_time)

class ArticleManager(models.Manager):
    def relevant(self):
        return self.filter(usercoding__relevant=True).distinct()

    def coded(self):
        return self.filter(usercoding__isnull=False).distinct()


class Article(models.Model):
    """
    Base article contents. Should never change after initial scraping
    """
    news_source = models.ForeignKey(NewsSource, null=True, db_index=True)
    url = models.CharField(max_length=1024, unique=True, db_index=True)
    title = models.TextField()
    author = models.CharField(max_length=1024, default="", blank=True)
    bodytext = models.TextField()
    orig_html = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = ArticleManager()

    # Fields from classification/coding- move to UserCoding
    relevant = models.NullBooleanField(db_index=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __unicode__(self):
        return self.url[:60]

    def is_coded(self):
        return hasattr(self, 'usercoding')

    def current_coding(self):
        return getattr(self, 'usercoding', None)

    def is_relevant(self):
        coding = self.current_coding()
        return coding and coding.relevant

    def get_categories(self):
        coding = self.current_coding()
        if coding:
            return coding.categories.all()
        else:
            return []

    # Deprecated, use news_source instead.
    feedname = models.CharField(max_length=1, editable=False, null=True, db_index=True)

class UserCoding(models.Model):
    article = models.OneToOneField(Article, db_index=True)
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, db_index=True, null=True, blank=True,
                             on_delete=models.SET_NULL)

    # Fields from classification/coding
    relevant = models.BooleanField()
    categories = models.ManyToManyField(Category, blank=True)

    class Meta:
        unique_together = (("article", "user"),)

#class TrainedCoding(models.Model):
#    article = models.OneToOneField(Article, db_index=True)
#    date = models.DateTimeField(auto_now=True)
#    model_info = models.TextField()
#
#    categories = models.ManyToManyField(Category, through='TrainedCategoryRelevance')
#    relevance = models.FloatField()
#
#class TrainedCategoryRelevance(models.Model):
#    coding = models.ForeignKey(TrainedCoding)
#    category = models.ForeignKey(Category)
#    relevance = models.FloatField()
#