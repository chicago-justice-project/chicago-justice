import logging
import datetime
import django.db

from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import Article, TrainedCoding, TrainedSentiment
from newsarticles.tagging import bin_article_for_sentiment, extract_sentiment_information

LOG = logging.getLogger(__name__)
MAX_API_CALLS = 5000
NUM_BINS = 5

def run():
    count = 0
    remaining_calls = MAX_API_CALLS
    current_bin = 1

    while remaining_calls > 0 and current_bin <= NUM_BINS:
        bin_articles = get_bin_articles(current_bin)
        count = bin_articles.count()
        if count > remaining_calls:
            bin_articles = bin_articles[:remaining_calls]
        for article in bin_articles:
            sent_json, entities = extract_sentiment_information(article.article.bodytext)
            TrainedSentiment.objects.create(coding=article, api_response=sent_json)
            for (ix, entity, sent_val) in entities:
                TrainedSentiment.objects.append(coding=article, police_entity_number=ix, police_entity_words=entity, sentiment=sent_val)

        remaining_calls = remaining_calls - count
        current_bin += 1

def get_bin_articles(current_bin):
    return TrainedCoding.objects.filter(bin=current_bin)
