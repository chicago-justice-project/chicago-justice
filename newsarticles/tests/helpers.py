from django.contrib.auth.models import User
from newsarticles.models import Article, NewsSource, Category

TEST_BODY = """
this is a long block of text for testing that article bodies get shortened for
non-logged-in users. Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

class DataFactory(object):
    """
    Helper class for instantiating model data in tests.
    """
    def make_category(self):
        return Category.objects.create(
            title='Guns',
            abbreviation='GUN',
            kind='crimes',
        )

    def make_admin(self):
        return User.objects.create_user(username='user1', password='12345', is_staff=True)

    def make_news_source(self):
        return NewsSource.objects.create(name='Daily Planet', short_name='planet')

    def make_article(self, title='Article title', news_source=None):
        if not news_source:
            news_source=NewsSource.objects.first()

        return Article.objects.create(
            news_source=news_source,
            url='http://example.com/1234',
            title=title,
            author='Clark Kent',
            bodytext=TEST_BODY)
