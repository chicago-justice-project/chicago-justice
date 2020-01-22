import logging
import datetime
import django.db

from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import Article, TrainedCoding, TrainedSentiment, TrainedSentimentEntities
from newsarticles.tagging import bin_article_for_sentiment,
                                 extract_sentiment_information,
                                 calculate_units,
                                 get_api_reponse,
                                 sent_evaller

LOG = logging.getLogger(__name__)
MAX_API_CALLS = 5000
NUM_BINS = sent_evaller.num_bins

def run():
    count = 0
    remaining_units = MAX_API_CALLS
    current_bin = 1
    bin_all_articles()
    assert remaining_units > 0
    while remaining_units > 0 and current_bin <= NUM_BINS:
        bin_articles = get_bin_articles(current_bin)
        articles_and_units = [(article, calculate_units(article.article.bodytext))
            for article in bin_articles]
        assert remaining_units > 0
        articles_to_run = []
        units_left_in_bin = remaining_units
        while units_left_in_bin:
            for art, units in articles_and_units:
                if units_left_in_bin - units:
                    articles_to_run.append((art, units))
                    units_left_in_bin -= units
                assert remaining_units > 0

        for article, units in articles_to_run:
            assert remaining_units > 0
            LOG.info("Title: {title}\n\tRemaining Calls: {remaining}\n\tLen: {length}\t\tUnits: {units}\n\n".format(title=article.article.title,
                                                                                                                remaining=remaining_units,
                                                                                                                length=len(article.article.bodytext),
                                                                                                                units=calculate_units(article.article.bodytext)))
            sent_json = get_api_reponse(article.article.bodytext)
            TrainedSentiment.objects.create(coding=article, api_response=sent_json)
            more_to_return = True
            while more_to_return:
                entity_tuple = extract_sentiment_information(sent_json)
                more_to_return = bool(entity_tuple)
                if more_to_return:
                    ix, entity, sent_val = entity_tuple
                    TrainedSentimentEntities.objects.create(coding=article, response=sent_json, index=ix, entity=entity, sentiment=sent_val)
            article.sentiment_processed = True
            remaining_units -= units
        current_bin += 1

def get_bin_articles(current_bin):
    return TrainedCoding.objects.filter(bin=current_bin,
                                        sentiment_processed=False)

def bin_all_articles():
    articles = TrainedCoding.objects.all()
    for article in articles:
        if 
