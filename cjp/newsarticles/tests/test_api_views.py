from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .helpers import DataFactory

from newsarticles.models import Article, NewsSource, Category


class ApiCategoryTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = DataFactory()
        cls.user = cls.factory.make_admin()
        cls.category = cls.factory.make_category()

    def test_get_categories(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/categories')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

        self.assertEqual(response.data.get('results'), [
            {
                'id': self.category.id,
                'title': self.category.title,
                'abbreviation': self.category.abbreviation,
                'kind': self.category.kind,
                'created': self.category.created.isoformat(),
            }
        ])

    def test_get_articles(self):
        article = self.factory.make_article(title='Test article')

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/articles')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

        article_result = response.data['results'][0]

        self.assertEqual(article_result.get('id'), article.id)
        self.assertEqual(article_result.get('title'), article.title)
        self.assertEqual(article_result.get('author'), article.author)
        self.assertEqual(article_result.get('bodytext'), article.bodytext)

    def test_get_article(self):
        article = self.factory.make_article(title='My test article')

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/articles/{}'.format(article.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), article.id)
        self.assertEqual(response.data.get('title'), article.title)
        self.assertEqual(response.data.get('author'), article.author)
        self.assertEqual(response.data.get('bodytext'), article.bodytext)


    def test_create_coding(self):
        article = self.factory.make_article(title='Test article')
        cat1 = self.factory.make_category()

        self.client.force_authenticate(user=self.user)

        coding = {
            'model_info': 'testcoder',
            'relevance': 0.25,
            # 'categories': {
            #     cat1.id : 0.8,
            # }
        }

        response = self.client.put(
            '/api/articles/{}/trained-coding'.format(article.id),
            data=coding
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        coding = article.trained_coding

        self.assertEqual(coding.relevance, 0.25)
