from django.core.exceptions import ObjectDoesNotExist
from functools import lru_cache
import json
import tagnews
from newsarticles.models import TrainedCategoryRelevance, TrainedCoding, Category

MIN_CATEGORY_RELEVANCE = 0.05

# Memoize taggers, they are slow to instantiate
@lru_cache(maxsize=1)
def crime_tagger():
    return tagnews.CrimeTags()

@lru_cache(maxsize=1)
def geo_tagger():
    return tagnews.GeoCoder()


def tag_article(article):
    location_text = tag_location(article)
    category_scores, max_score = tag_categories(article)

    data = {
        'model_info': 'tagnews {}'.format(tagnews.__version__),
        'relevance': max_score,
        'location_text': location_text,
    }

    coding, exists = TrainedCoding.objects.update_or_create(
        defaults=data,
        article=article
    )

    TrainedCategoryRelevance.objects.filter(coding=coding.id).delete()
    for (category, relevance) in category_scores:
        TrainedCategoryRelevance.objects.create(
            coding=coding,
            category=category,
            relevance=relevance
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
            print("category not found: {}".format(abbr))

    return category_scores, max_score

def tag_location(article):
    if len(article.bodytext) < 10:
        return '[]'

    tokenized_locations = geo_tagger().extract_geostrings(article.bodytext,
                                                          prob_thresh=0.5)

    strings = [' '.join(tokens) for tokens in tokenized_locations]

    return json.dumps(strings)
