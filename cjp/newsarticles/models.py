from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from itertools import groupby
from collections import OrderedDict

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


@python_2_unicode_compatible
class NewsSource(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256, db_index=True)
    legacy_feed_id = models.CharField(max_length=8, blank=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)


@python_2_unicode_compatible
class Category(models.Model):

    KINDS = OrderedDict([
        ('crimes', 'Crimes'),
        ('orgs', 'Justice Agencies / Agencies'),
        ('policing', 'Policing'),
        ('other', 'Misc.'),
    ])
    DEFAULT_KIND = 'other'

    title = models.CharField(max_length=256)
    abbreviation = models.CharField(max_length=5)
    active = models.BooleanField(default=True)
    kind = models.CharField(max_length=50, choices=KINDS.items(), default=DEFAULT_KIND)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = CategoryQuerySet.as_manager()

    def __str__(self):
        return '{} ({})'.format(self.title, self.abbreviation)

    class Meta:
        ordering = ['kind', 'abbreviation']


@python_2_unicode_compatible
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

    def __str__(self):
        return '{} - {}'.format(self.news_source.name, self.completed_time)

class ArticleQuerySet(models.QuerySet):
    def exclude_irrelevant(self):
        return self.exclude(usercoding__relevant=False)

    def relevant(self):
        return self.filter(usercoding__relevant=True)

    def coded(self):
        return self.filter(usercoding__isnull=False)

    def uncoded(self):
        return self.filter(usercoding__isnull=True)

    def filter_categories(self, categories):
        return self.filter(usercoding__categories__in=categories)


@python_2_unicode_compatible
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

    objects = ArticleQuerySet.as_manager()

    # Fields from classification/coding- move to UserCoding
    relevant = models.NullBooleanField(db_index=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
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
    locations = models.TextField(default='[]', blank=True)

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