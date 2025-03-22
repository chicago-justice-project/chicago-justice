from __future__ import unicode_literals

from itertools import groupby
from collections import OrderedDict

from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 1 and obj.pk != model.objects.get().pk):
        raise ValidationError("Can only create 1 {} instance".format(model.__name__))


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
    kind = models.CharField(
        max_length=50, choices=KINDS.items(), default=DEFAULT_KIND)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = CategoryQuerySet.as_manager()

    def __str__(self):
        return '{} ({})'.format(self.title, self.abbreviation)

    class Meta:
        ordering = ['kind', 'abbreviation']


class ScraperResult(models.Model):
    """
    A single run of a scraper.
    """
    news_source = models.ForeignKey(NewsSource, db_index=True, on_delete=models.PROTECT)

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

    def relevant_trained(self):
        return self.filter(trainedcoding__relevance__gt=0.5)

    def relevant_cpd_trained(self):
        return self.filter(trainedcoding__trainedcategoryrelevance__category=2, trainedcoding__trainedcategoryrelevance__relevance__gt=0.5)

    def relevant(self):
        return self.filter(usercoding__relevant=True)

    def coded(self):
        return self.filter(usercoding__isnull=False)

    def uncoded(self):
        return self.filter(usercoding__isnull=True)

    def filter_categories(self, categories):
        return self.filter(Q(usercoding__categories__in=categories) | Q(trainedcoding__trainedcategoryrelevance__category__in=categories)).distinct()

    def filter_relevant_trained(self, relevance=0.85):
        return self.filter(trainedcoding__relevance__gte=relevance)

    def filter_trained_categories(self, categories, relevance=0.85):
        return self.filter(trainedcoding__trainedcategoryrelevance__category__in=categories, trainedcoding__trainedcategoryrelevance__relevance__gte=relevance)


class Article(models.Model):
    """
    Base article contents. Should never change after initial scraping
    """
    news_source = models.ForeignKey(NewsSource, null=True, db_index=True, on_delete=models.SET_NULL)
    url = models.CharField(max_length=1024, unique=True, db_index=True)
    title = models.TextField()
    author = models.CharField(max_length=1024, default="", blank=True)
    bodytext = models.TextField()
    orig_html = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    # Fields from classification/coding- move to UserCoding
    relevant = models.BooleanField(db_index=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.url[:90]

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
    feedname = models.CharField(
        max_length=1, editable=False, null=True, db_index=True)


SENTIMENT_CHOICES = (
    (None, 'Not coded'),
    (1, 'Positive'),
    (0, 'Neutral'),
    (-1, 'Negative'),
)

RACE_CHOICES = (
    (None, ""),
    ("WHI", "White"),
    ("BAA", "Black or African American"),
    ("AIAN", "American Indian or Alaska Native"),
    ("ASIA", "Asian"),
    ("NHPI", "Native Hawaiian or Other Pacific Islander"),
    ("OTH", "Other"),
    ("UND", "Undetermined"),
)

ETHNICITY_CHOICES = (
    (None, ""),
    ("HISPA", "Hispanic or Latino"),
    ("NOHIS", "Not Hispanic or Latino"),
    ("UND", "Undetermined"),
)

SEX_CHOICES = (
    (None, ""),
    ("MALE", "Male"),
    ("FEMALE", "Female"),
    ("TRANM", "Transgender Male"),
    ("TRANF", "Transgender Female"),
    ("UND", "Undetermined"),
)

WEAP_CHOICES = (
    (None, ""),
    ("FIRE", "Firearms (handguns, rifles, shotguns)"),
    ("KNIF", "Knives/cutting instruments"),
    ("OTH", "Other weapon"),
    ("PERS", "Personal weapons"),
    ("ARM", "Strong-arm (hands/fists/other)"),
    ("UND", "Undetermined"),
)

class UserCoding(models.Model):
    article = models.OneToOneField(Article, db_index=True, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, db_index=True, null=True, blank=True,
                             on_delete=models.SET_NULL)

    # Fields from classification/coding
    relevant = models.BooleanField()
    categories = models.ManyToManyField(Category, blank=True)
    locations = models.TextField(default='[]', blank=True)
    sentiment = models.IntegerField(
        blank=True, null=True, choices=SENTIMENT_CHOICES)

    # Fields for victim/offender trait information
    vict_age = models.PositiveIntegerField(blank=True)
    vict_race = models.CharField(max_length=128, choices=RACE_CHOICES, default=None)
    vict_ethnicity = models.CharField(max_length=32, choices=ETHNICITY_CHOICES, default=None)
    vict_sex = models.CharField(max_length=32, choices=SEX_CHOICES, default=None)
    vict_name = models.CharField(max_length=128, blank=True)

    offend_age = models.PositiveIntegerField(blank=True, null=True)
    offend_race = models.CharField(max_length=128, choices=RACE_CHOICES, default=None)
    offend_ethnicity = models.CharField(max_length=32, choices=ETHNICITY_CHOICES, default=None)
    offend_sex = models.CharField(max_length=32, choices=SEX_CHOICES, default=None)
    offend_name = models.CharField(max_length=128, blank=True)
    offend_weap = models.CharField(max_length=128, choices=WEAP_CHOICES, default=None)

    class Meta:
        unique_together = (("article", "user"),)


class TrainedCoding(models.Model):
    article = models.OneToOneField(Article, db_index=True, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now=True)
    model_info = models.TextField()

    categories = models.ManyToManyField(
        Category, through='TrainedCategoryRelevance')
    relevance = models.FloatField()
    sentiment = models.FloatField(null=True)
    bin = models.IntegerField(null=True, blank=True)
    sentiment_processed = models.BooleanField(default=False)


class TrainedLocation(models.Model):
    coding = models.ForeignKey(TrainedCoding, null=True, on_delete=models.SET_NULL)
    text = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    neighborhood = models.TextField(default="", blank=True)
    is_best = models.BooleanField(default=False)


class TrainedCategoryRelevance(models.Model):
    coding = models.ForeignKey(TrainedCoding, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    relevance = models.FloatField()


class TrainedSentiment(models.Model):
    coding = models.ForeignKey(TrainedCoding, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now=True)
    api_response = models.TextField()

class TrainedSentimentEntities(models.Model):
    coding = models.ForeignKey(TrainedCoding, null=True, on_delete=models.SET_NULL)
    response = models.ForeignKey(TrainedSentiment, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)
    entity = models.TextField(blank=True)
    sentiment = models.FloatField(null=True, blank=True)

class SentimentCallsCounter(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    remaining_calls = models.PositiveIntegerField(default=0)

    def clean(self):
        validate_only_one_instance(self)
