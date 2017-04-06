from __future__ import unicode_literals

from django.db import models
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
    author = models.CharField(max_length=1024, default="")
    bodytext = models.TextField()
    orig_html = models.TextField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = ArticleManager()

    # Fields from classification/coding- move to UserCoding
    relevant = models.NullBooleanField(db_index=True)
    categories = models.ManyToManyField(Category)

    def __unicode__(self):
        return self.url[:60]

    def is_coded(self):
        return self.usercoding_set.count() > 0


class UserCoding(models.Model):
    article = models.ForeignKey(Article, db_index=True)
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, db_index=True)

    # Fields from classification/coding
    relevant = models.BooleanField()
    categories = models.ManyToManyField(Category)

    class Meta:
        unique_together = (("article", "user"),)
        permissions = (('can_code_article', 'Can code news articles'),)

#class LearnedCoding(models.Model):
#    article = models.ForeignKey(Article, unique=True)
#    date = models.DateTimeField(auto_now=True)
#    model_info = models.TextField()
#
#    categories = models.ManyToManyField(Category, through='LearnedCategoryRelevance')
#    relevance = models.FloatField()
#
#class LearnedCategoryRelevance(models.Model):
#    coding = models.ForeignKey(LearnedCoding)
#    category = models.ForeignKey(Category)
#    relevance = models.FloatField()
#