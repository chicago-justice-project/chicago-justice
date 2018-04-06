import logging

from newsarticles.tagging import tag_article, current_model_info
from newsarticles.models import Article
from newsarticles.utils.migration import queryset_iterator

LOG = logging.getLogger(__name__)

def run():
    outdated_articles = Article.objects.exclude(
        trainedcoding__model_info=current_model_info()
    )

    count = 0

    total = outdated_articles.count()

    LOG.info('Tagging %d articles', total)

    for article in queryset_iterator(outdated_articles, chunksize=500):
        tag_article(article)

        count += 1

        if count % 1000 == 1:
            LOG.info('Tagging article %d of %d', count, total)

    LOG.info('Done tagging %d articles', count)
