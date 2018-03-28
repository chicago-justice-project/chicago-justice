from __future__ import unicode_literals
from functools import lru_cache
import logging
from django.core.exceptions import ObjectDoesNotExist
import tagnews

from newsarticles.models import TrainedCategoryRelevance, TrainedCoding, TrainedLocation, Category

MIN_CATEGORY_RELEVANCE = 0.05
MIN_LOCATION_RELEVANCE = 0.5

LOG = logging.getLogger(__name__)

# Memoize taggers, they are slow to instantiate
@lru_cache(maxsize=1)
def crime_tagger():
    return tagnews.CrimeTags()

@lru_cache(maxsize=1)
def geo_tagger():
    return tagnews.GeoCoder()

def current_model_info():
    return 'tagnews {}'.format(tagnews.__version__)

def tag_article(article):
    locations = tag_locations(article)
    category_scores, max_score = tag_categories(article)

    TrainedCoding.objects.filter(article=article).delete()

    coding = TrainedCoding.objects.create(
        article=article,
        model_info=current_model_info(),
        relevance=max_score
    )

    for (category, relevance) in category_scores:
        if (relevance > MIN_CATEGORY_RELEVANCE):
            TrainedCategoryRelevance.objects.create(
                coding=coding,
                category=category,
                relevance=relevance
            )

    for location in locations:
        TrainedLocation.objects.create(
            coding=coding,
            text=location
        )

def tag_categories(article):
    if len(article.bodytext) < 10:
        return [], 0

    probs = crime_tagger().tagtext_proba(article.bodytext)

    category_scores = []
    max_score = 0

    for abbr, score in zip(probs.index, probs.values):
        try:
            category = Category.objects.get(abbreviation=abbr)
            category_scores.append((category, score))
            max_score = max(score, max_score)
        except ObjectDoesNotExist:
            LOG.warn('category not found: %s', abbr)

    return category_scores, max_score

def tag_locations(article):
    if len(article.bodytext) < 10:
        return []

    tokenized_locations = geo_tagger().extract_geostrings(
        article.bodytext,
        prob_thresh=MIN_LOCATION_RELEVANCE
    )

    return [' '.join(tokens) for tokens in tokenized_locations]
