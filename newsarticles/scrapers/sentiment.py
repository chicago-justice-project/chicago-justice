import logging
import datetime
import django.db

from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import Article, Category, UserCoding, TrainedCoding, TrainedCategoryRelevance, TrainedSentiment, TrainedSentimentEntities, SentimentCallsCounter
from newsarticles.tagging import bin_article_for_sentiment, extract_sentiment_information, calculate_units, get_api_reponse, sent_evaller

LOG = logging.getLogger(__name__)
MAX_API_CALLS = 200
NUM_BINS = sent_evaller().num_bins

def analyze_all_articles():
    count = 0
    current_bin = 0
    try:
        remaining_units_obj, created = SentimentCallsCounter.objects.get_or_create(defaults={'remaining_calls': MAX_API_CALLS})
        if not created:
            if new_month(remaining_units_obj):
                reset_counter(remaining_units_obj, MAX_API_CALLS)
        remaining_units = remaining_units_obj.remaining_calls
    except:
        LOG.warn('No API call counter exists')
        remaining_units = 0
    assert remaining_units > 0
    while remaining_units > 0 and current_bin < NUM_BINS:
        print(f"remaining units {remaining_units},\t Current bin: {current_bin}")
        bin_articles = get_bin_articles(current_bin)
        print(f"num arts in bin: {len(bin_articles)}")
        articles_and_units = [(article, calculate_units(article.article.bodytext))
            for article in bin_articles]
        assert remaining_units > 0
        articles_to_run = []
        units_left_in_bin = remaining_units
        if bin_articles:
            while units_left_in_bin > 0:
                print(f"units_left_in_bin: {units_left_in_bin}")
                print(f"articles to run count {len(articles_to_run)}")
                for art, units in articles_and_units:
                    if (units_left_in_bin - units) > 0:
                        articles_to_run.append((art, units))
                    units_left_in_bin -= units
                    assert remaining_units > 0

        for (article, units) in articles_to_run:
            assert remaining_units > 0
            LOG.info("Title: {title}\n\tRemaining Calls: {remaining}\n\tLen: {length}\t\tUnits: {units}\n\n".format(title=article.article.title,
                                                                                                                remaining=remaining_units,
                                                                                                                length=len(article.article.bodytext),
                                                                                                                units=calculate_units(article.article.bodytext)))
            sent_json = get_api_reponse(article.article.bodytext)
            remaining_units_obj.remaining_calls = remaining_units - units
            remaining_units_obj.save() #need to use save() rather than update() to auto update last_updated to now
            TrainedSentiment.objects.create(coding=article, api_response=sent_json)
            entity_tuple = extract_sentiment_information(sent_json)
            for ix, entity, sent_val in entity_tuple:
                print(ix, entity, sent_val)
                TrainedSentimentEntities.objects.create(coding=article, response=sent_json, index=ix, entity=entity, sentiment=sent_val)
            article.update(sentiment_processed=True)
            remaining_units = remaining_units_obj.remaining_calls
        current_bin += 1

def get_bin_articles(current_bin):
    return TrainedCoding.objects.filter(bin=current_bin,
                                        sentiment_processed=False)

def bin_all_articles():
    articles = Article.objects.all()
    for article in articles:
        cpd_user_val = 0
        cpd_trained_val = 0
        try:
            user_coding = UserCoding.objects.get(article=article)
        except ObjectDoesNotExist:
            user_coding = False
        try:
            trained_coding = TrainedCoding.objects.get(article=article)
        except ObjectDoesNotExist:
            LOG.warn('No trained coding exists for article: %s', article.title)
            trained_coding = False
        if user_coding:
            cpd_user_val = 1 if user_coding.categories.filter(abbreviation='CPD').exists() else 0
        if trained_coding:
            try:
                trained_coding_cats = TrainedCategoryRelevance.objects.filter(coding=trained_coding)
            except:
                LOG.warn('Trained coding of article contains no categories')
                trained_coding_cats = False
            if trained_coding_cats:
                for cat in trained_coding_cats:
                    if 'CPD' in str(cat.category):
                        cpd_trained_val = cat.relevance
        trained_coding.bin = bin_article_for_sentiment(article, cpd_user_val, cpd_trained_val)
        trained_coding.save()

def new_month(last_call_obj):
    now = datetime.datetime.now()
    last_call_datetime = last_call_obj.last_updated
    if now.year - last_call_datetime.year:
        return True
    elif now.year == last_call_datetime.year and now.month - last_call_datetime.month > 0:
        return True
    else:
        return False

def reset_counter(last_call_obj, max_calls=0):
    try:
        last_call_obj.remaining_calls = max_calls
        last_call_obj.save() #need to use save() rather than update() to auto update last_updated to now
    except:
        LOG.warn('Could not reset API counter')
