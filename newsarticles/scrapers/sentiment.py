import logging
import datetime
from math import floor
import django.db

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from newsarticles.models import Article, UserCoding, TrainedCoding, TrainedCategoryRelevance, TrainedSentiment, TrainedSentimentEntities, SentimentCallsCounter
from newsarticles.tagging import bin_article_for_sentiment, extract_sentiment_information, calculate_units, get_api_reponse, sent_evaller
from newsarticles.utils.migration import queryset_iterator

LOG = logging.getLogger(__name__)
MAX_API_CALLS = floor(5000/31)  # 5000 units split over one month (31 days)
NUM_BINS = sent_evaller().num_bins

def analyze_all_articles():
    current_bin = 0
    try:
        remaining_units_obj, created = SentimentCallsCounter.objects.get_or_create(defaults={'remaining_calls': MAX_API_CALLS})
        if not created:
            if new_day(remaining_units_obj):
                reset_counter(remaining_units_obj, MAX_API_CALLS)
        remaining_units = remaining_units_obj.remaining_calls
    except:
        LOG.warn('No API call counter exists')
        remaining_units = 0
    assert remaining_units > 0
    while remaining_units > 0 and current_bin < NUM_BINS:
        LOG.info(f"remaining units {remaining_units},\t Current bin: {current_bin}")
        bin_articles = get_bin_articles(current_bin)
        LOG.info(f"num arts in bin: {len(bin_articles)}")
        articles_to_run = []
        units_left_in_bin = remaining_units
        for article in queryset_iterator(bin_articles, chunksize=500):
            assert remaining_units > 0
            if units_left_in_bin > 0:
                assert remaining_units > 0
                units = calculate_units(article.article.bodytext)
                LOG.info(f"units_left_in_bin: {units_left_in_bin}")
                LOG.info(f"articles to run count: {len(articles_to_run)}")
                if (units_left_in_bin - units) > 0:
                    articles_to_run.append((article, units))
                units_left_in_bin -= units

        for (article, units) in articles_to_run:
            assert remaining_units > 0
            LOG.info("Title: {title}\n\tRemaining Calls: {remaining}\n\tLen: {length}\t\tUnits: {units}\n\n".format(title=article.article.title,
                                                                                                                remaining=remaining_units,
                                                                                                                length=len(article.article.bodytext),
                                                                                                                units=calculate_units(article.article.bodytext)))
            sent_json = get_api_reponse(article.article.bodytext)
            remaining_units_obj.remaining_calls = remaining_units - units
            remaining_units_obj.save() #need to use save() rather than update() to auto update last_updated to now
            trained_sent = TrainedSentiment.objects.create(coding=article, api_response=sent_json)
            entity_tuple = extract_sentiment_information(sent_json)
            for ix, entity, sent_val in entity_tuple:
                TrainedSentimentEntities.objects.create(coding=article, response=trained_sent, index=ix, entity=entity, sentiment=sent_val)
            article.sentiment_processed=True
            article.save()
            remaining_units = remaining_units_obj.remaining_calls
        current_bin += 1

def get_bin_articles(current_bin):
    return TrainedCoding.objects.filter(bin=current_bin,
                                        sentiment_processed=False)

def bin_all_articles():
    articles = Article.objects.all()
    count = 0
    total = articles.count()
    LOG.info('Binning %d articles', total)
    for article in queryset_iterator(articles, chunksize=500):
        count += 1
        if count % 1000 == 1:
            LOG.info('Binning article %d of %d', count, total)
        bin_article(article)
    LOG.info('Done binning %d articles', count)

def bin_updated_articles():
    try:
        last_call_datetime = SentimentCallsCounter.objects.get().last_updated
    except:
        LOG.warn('No SentimentCallsCounter object exists')
        last_call_datetime = datetime.datetime.now() # default to right now
    articles = Article.objects.filter(Q(trainedcoding__bin=None) | Q(usercoding__date__gte=last_call_datetime)).distinct()
    count = 0
    total = articles.count()
    LOG.info('Binning %d unbinned or updated articles', total)
    for article in queryset_iterator(articles, chunksize=500):
        count += 1
        if count % 1000 == 1:
            LOG.info('Binning article %d of %d', count, total)
        bin_article(article)
    LOG.info('Done binning %d unbinned or updated articles', count)

def bin_article(article):
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

def new_day(last_call_obj):
    now = datetime.datetime.now()
    last_call_datetime = last_call_obj.last_updated
    # Assume that if day isn't the same it's a new future day
    return now.day != last_call_datetime.day

def reset_counter(last_call_obj, max_calls=0):
    try:
        last_call_obj.remaining_calls = max_calls
        last_call_obj.save()  # need to use save() rather than update() to auto update last_updated to now
    except:
        LOG.warn('Could not reset API counter')
