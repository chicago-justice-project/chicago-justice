import logging
import datetime
import django.db

from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import Article, TrainedCoding, TrainedSentiment
from newsarticles.tagging import bin_article_for_sentiment,
                                 extract_sentiment_information,
                                 calculate_units

LOG = logging.getLogger(__name__)
MAX_API_CALLS = 5000
NUM_BINS = 5

def run():
    count = 0
    remaining_calls = MAX_API_CALLS
    current_bin = 1

    while remaining_calls > 0 and current_bin <= NUM_BINS:
        bin_articles = get_bin_articles(current_bin)
        articles_and_units = [(article, calculate_units(article))
            for article in bin_articles]

        articles_to_run = []
        units_left_in_bin = remaining_calls
        while units_left_in_bin:
            for art, units in articles_and_units:
                if units_left_in_bin - units:
                    articles_to_run.append((art, units))
                    units_left_in_bin -= units

        for article, units in articles_to_run:
            sent_json = get_api_reponse(article.article.bodytext)
            TrainedSentiment.objects.create(coding=article, api_response=sent_json)
            more_to_return = True
            while more_to_return:
                entity_tuple = extract_sentiment_information(article.article.bodytext)
                more_to_return = bool(entity_tuple)
                if more_to_return:
                    ix, entity, sent_val = entity_tuple
                    TrainedSentiment.objects.append(coding=article, police_entity_number=ix, police_entity_words=entity, sentiment=sent_val)
            remaining_calls -= units
        current_bin += 1

def get_bin_articles(current_bin):
    return TrainedCoding.objects.filter(bin=current_bin)
