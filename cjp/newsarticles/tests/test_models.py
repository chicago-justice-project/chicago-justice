from django.test import TestCase

from .models import Article, UserCoding, NewsSource

class ArticleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        news_source = NewsSource.objects.create(short_name='mysource')
        cls.article = Article.objects.create(news_source_id=news_source,
                                             url='http://example.com/article1',
                                             title='Man bites dog',
                                             relevant=True,
                                             bodytext='The man bit the dog')

    def test_uncoded(self):
        self.assertFalse(self.article.is_coded())

    def test_coded(self):
        UserCoding.objects.create(
            article=self.article,
            user_id=0,
            relevant=True,
        )

        self.assertTrue(self.article.is_coded())

