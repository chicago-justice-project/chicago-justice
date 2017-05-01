from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from newsarticles.models import Article, NewsSource
from newsarticles.views import view_article, code_article

TEST_BODY = """
this is a long block of text for testing that article bodies get shortened for
non-logged-in users. Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

class ViewArticleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='user1', password='12345')
        user1.save()

        news_source = NewsSource.objects.create(name='Daily Planet',
                                                short_name='planet')
        cls.article = Article.objects.create(news_source=news_source,
                                             url='http://example.com/1234',
                                             title='Man bites dog',
                                             author='Clark Kent',
                                             bodytext=TEST_BODY)

    def test_url_exists(self):
        url = '/articles/{}/'.format(self.article.id)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_reverse_resolve(self):
        resp = self.client.get(reverse('view-article', args=[self.article.id]))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_preview_text(self):
        resp = self.client.get(reverse('view-article', args=[self.article.id]))

        self.assertEqual(resp.context['is_preview'], True)
        # First 300 chars plus '...'
        self.assertEqual(len(resp.context['display_text']), 303)

    def test_logged_in_full_text(self):
        login = self.client.login(username='user1', password='12345')
        resp = self.client.get(reverse('view-article', args=[self.article.id]))

        self.assertEqual(resp.context['is_preview'], False)
        self.assertEqual(len(resp.context['display_text']), len(TEST_BODY))
