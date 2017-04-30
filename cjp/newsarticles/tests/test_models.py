from uuid import uuid4
from django.test import TestCase

from newsarticles.models import Article, UserCoding, NewsSource, Category

def make_article(save=True):
    url = 'http://example.com/{}'.format(uuid4())
    article = Article(news_source_id=0, url=url, title='', bodytext='', relevant=True)

    if save:
        article.save()
    return article

def make_category(save=True):
    cat = Category(category_name="", abbreviation="")
    if save:
        cat.save()
    return cat

class ArticleTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.article = make_article()
        cls.categories = [make_category(), make_category(), make_category()]

    def test_is_coded_uncoded(self):
        self.assertFalse(self.article.is_coded())

    def test_is_coded_coded(self):
        UserCoding.objects.create(
            article=self.article,
            user_id=0,
            relevant=True,
        )

        self.assertTrue(self.article.is_coded())

    def test_relevant_uncoded(self):
        self.assertIsNone(self.article.is_relevant())

    def test_relevant_one_coding_true(self):
        UserCoding.objects.create(
            article=self.article,
            user_id=0,
            relevant=True,
        )
        self.assertTrue(self.article.is_relevant())

    def test_relevant_one_coding_false(self):
        UserCoding.objects.create(
            article=self.article,
            user_id=0,
            relevant=False,
        )
        self.assertFalse(self.article.is_relevant())

    def test_categories_uncoded(self):
        self.assertEqual(len(self.article.get_categories()), 0)

    def test_categories_coded(self):
        expected_categories = [self.categories[0]]

        coding = UserCoding.objects.create(
            article=self.article,
            user_id=0,
            relevant=True,
        )
        coding.categories = expected_categories
        coding.save()

        categories = self.article.get_categories()
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].id, expected_categories[0].id)


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
