from uuid import uuid4
from django.test import TestCase

from newsarticles.models import Article, UserCoding, NewsSource

def make_article(save=True):
    url = 'http://example.com/{}'.format(uuid4())
    article = Article(news_source_id=0, url=url, title='', bodytext='', relevant=True)

    if save:
        article.save()
    return article

class ArticleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article = make_article()

    def test_uncoded(self):
        self.assertFalse(self.article.is_coded())

    def test_coded(self):
        UserCoding.objects.create(
            article=self.article,
            user_id=0,
            relevant=True,
        )

        self.assertTrue(self.article.is_coded())

class ArticleManagerTest(TestCase):
    """
    Tests querysets on the ArticleManager
    """
    @classmethod
    def setUpTestData(cls):
        a1 = make_article()
        a2 = make_article()
        a3 = make_article()

        UserCoding.objects.create(article=a1, user_id=0, relevant=True)
        UserCoding.objects.create(article=a2, user_id=0, relevant=False)

    def test_relevant_queryset(self):
        queryset = Article.objects.relevant()
        self.assertEqual(queryset.count(), 1)

    def test_coded_queryset(self):
        queryset = Article.objects.coded()
        self.assertEqual(queryset.count(), 2)

    def test_all_queryset(self):
        queryset = Article.objects.all()
        self.assertEqual(queryset.count(), 3)
