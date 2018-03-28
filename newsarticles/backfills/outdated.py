import logging

from newsarticles.tagging import tag_article, current_model_info
from newsarticles.models import Article

LOG = logging.getLogger(__name__)

def run():
    outdated_articles = Article.objects.exclude(
        trainedcoding__model_info=current_model_info()
    )

    count = 0
    total = outdated_articles.count()

    for article in outdated_articles:
        tag_article(article)

        count += 1

        if count % 100 == 1:
            LOG.info('Tagging article %d of %d', count, total)

    LOG.info('Done tagging %d articles', count)
