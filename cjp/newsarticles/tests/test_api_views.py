from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .helpers import TestFactory

from newsarticles.models import Article, NewsSource, Category


class ApiCategoryTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = TestFactory()

    def test_get_categories(self):
        self.client.force_authenticate(user=self.data.admin)

        response = self.client.get('/api/categories')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

        category = self.data.category
        self.assertEqual(response.data.get('results'), [
            {
                'id': category.id,
                'title': category.title,
                'abbreviation': category.abbreviation,
                'kind': category.kind,
                'created': category.created.isoformat(),
            }
        ])

    def test_get_articles(self):
        self.client.force_authenticate(user=self.data.admin)

        response = self.client.get('/api/articles')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 1)

        article = self.data.article
        self.assertEqual(response.data.get('results'), [
            {
                'id': article.id,
                'title': article.title,
                'bodytext': article.bodytext,
                'author': article.author,
            }
        ])

    def test_get_article(self):
        self.client.force_authenticate(user=self.data.admin)
        id = self.data.article.id

        response = self.client.get('/api/articles/{}'.format(id))


    def test_create_coding(self):
        self.client.force_authenticate(user=self.data.admin)
        id = self.data.article.id

        response = self.client.put('/api/articles/{}/trained-coding')
