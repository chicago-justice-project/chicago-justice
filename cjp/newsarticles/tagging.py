import tagnews
from newsarticles.models import TrainedCategoryRelevance, TrainedCoding, Category

# Lazy load taggers, no need to re-instantiate during the lifetime of the process
crime_tagger = None
geo_extractor = None

def init_taggers():
    if crime_tagger is None:
        crime_tagger = tagnews.CrimeTags()

    # if geo_extractor is None:
    #     geo_extractor = tagnews.GeoCoder()


def tag_article(article):
    init_taggers()

    location_text = '' # tag_location(article)
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
    for (category_id, relevance) in category_scores:
        TrainedCategoryRelevance.objects.create(
            coding=coding,
            category=category_id,
            relevance=relevance
        )


def tag_categories(article):
    probs = crime_tagger.tagtext_proba(article.body)

    category_scores = []
    max_score = 0

    for abbr, score in zip(probs.index, probs.values):
        category = Category.objects.find(abbreviation=abbr)
        if category:
            category_scores.append((category.id, score))
            max_score = max(score, max_score)

    return category_scores, max_score

def tag_location(article):
    strings = geo_extractor.extract_geostrings(article.body, prob_thresh=0.5)

    if len(strings) < 1:
        return ''

    return ' '.join(strings[0])
