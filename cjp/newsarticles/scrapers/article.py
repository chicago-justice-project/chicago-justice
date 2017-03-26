from __future__ import unicode_literals
import logging
import time
import html2text

from django.core.exceptions import ObjectDoesNotExist
from newsarticles.models import Article, NewsSource, ScraperResult
from .util import get_rss_links, get_html_links, load_html, get_rss_articles

FAKE_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

LOG = logging.getLogger(__name__)

class ScraperException(Exception):
    pass

class ArticleResult(object):
    CREATED = 'created'
    EXISTS = 'exists'
    SKIPPED = 'skipped'
    ERROR = 'error'
    UNKNOWN = 'unknown'

    def __init__(self, url, status=UNKNOWN, article=None, error=None):
        self.url = url
        self.article = article
        self.status = status
        self.error = error

        if self.error and self.status == ArticleResult.UNKNOWN:
            self.status = ArticleResult.ERROR

    @property
    def success(self):
        return self.status not in [ArticleResult.ERROR, ArticleResult.UNKNOWN]

    def __repr__(self):
        return 'success={} status={} url={}'.format(self.success, self.status, self.url)

def scrape_articles(scrapers):
    for cfg in scrapers:
        LOG.info('Running scraper %s', cfg)
        scraper = ArticleScraper(config=cfg)
        result = scraper.run()
        if result.success:
            LOG.info('%s - successful added=%i error=%i',
                     result.news_source, result.added_count, result.error_count)
        else:
            LOG.warn('%s - failed: %s', result.news_source, result.output)


class ArticleScraper(object):
    '''Default scraper implementation. Uses CSS selectors to pick out links from an
    index page, article title, and article text. Also supports RSS indexes.'''
    def __init__(self, config=None):
        config = config or dict()
        self.index_url = config['index_url']
        self.enabled = config.get('enabled', True)
        self.rss_index = config.get('rss_index', False)
        self.rss_articles = config.get('rss_articles', False)
        self.index_url_selector = config.get('index_url_selector', 'link')
        self.fake_user_agent = config.get('fake_user_agent', False)
        self.use_cookies = config.get('use_cookies', False)

        self.title_selector = config.get('title_selector', None)
        self.body_selector = config.get('body_selector', None)
        self.author_selector = config.get('author_selector', None)
        self.exclude_selector = config.get('exclude_selector', None)

        self.html2text = html2text.HTML2Text()
        self.html2text.body_width = 80
        self.html2text.inline_links = False

        news_source_name = config['news_source']
        try:
            news_source = NewsSource.objects.get(short_name=news_source_name)
        except ObjectDoesNotExist:
            news_source = NewsSource(name=news_source_name, short_name=news_source_name)
            LOG.info('News source %s not found, creating', news_source_name)
            news_source.save()

        self.news_source = news_source

    def make_scraper_result(self, article_results):
        result = ScraperResult(news_source=self.news_source, added_count=0, error_count=0,
                               total_count=0, output='')
        for article_res in article_results:
            result.total_count += 1

            if article_res.status == ArticleResult.CREATED:
                result.added_count += 1
            if article_res.error:
                result.error_count += 1
                result.output += 'Error: {} [{}]\n'.format(article_res.error, article_res.url)

        # Avoid divide by zero
        error_rate = result.error_count / max(result.total_count, 1)

        result.success = result.total_count > 0 and error_rate < 0.25

        return result

    def run(self, delay_sec=1, save=True, skip_existing=True):
        results = []
        try:
            articles = self.read_articles(skip_existing)
        except Exception, e:
            result = ScraperResult(news_source=self.news_source, success=False)
            result.output = 'Error getting article listing: {}'.format(e)
            result.save()
            return result

        for result in articles:
            LOG.debug('result: %s', result)

            if save and result.article and result.success:
                result.article.save()
            results.append(result)

            if result.status != ArticleResult.SKIPPED:
                time.sleep(delay_sec)

        scraper_result = self.make_scraper_result(results)
        scraper_result.save()
        return scraper_result

    def read_articles(self, skip_existing=True):
        if not self.enabled:
            LOG.warn('Scraper disabled, skipping')
            return

        if self.rss_articles:
            return self.read_rss_articles(skip_existing)

        if self.rss_index:
            urls = get_rss_links(self.index_url, self.index_url_selector)
        else:
            urls = get_html_links(self.index_url, self.index_url_selector)

        return self.read_html_articles(urls, skip_existing)

    def read_rss_articles(self, skip_existing):
        for rss_article in get_rss_articles(self.index_url):
            yield self.process_rss_article(rss_article)

    def read_html_articles(self, urls, skip_existing):
        for url in urls:
            yield self.process_link(url, skip_existing)

    def process_rss_article(self, rss_article):
        url = rss_article.link
        try:
            existing_article = Article.objects.get(url=url)
        except ObjectDoesNotExist:
            existing_article = None

        if existing_article:
            return ArticleResult(url, status=ArticleResult.SKIPPED)

        article = Article(url=url, news_source=self.news_source, relevant=True)
        article.title = rss_article.title
        article.author = rss_article.author
        article.orig_html = rss_article.content[0]['value']
        article.bodytext = self.html2text.handle(article.orig_html)

        return ArticleResult(url=url, status=ArticleResult.CREATED, article=article)

    def process_link(self, url, skip_existing):
        '''Attempts to load a URL and extract a news story'''

        try:
            existing_article = Article.objects.get(url=url)
        except ObjectDoesNotExist:
            existing_article = None

        if existing_article and skip_existing:
            return ArticleResult(url, status=ArticleResult.SKIPPED)

        headers = []
        if self.fake_user_agent:
            headers.append(('User-agent', FAKE_USER_AGENT))

        try:
            soup = load_html(url, headers=headers, with_cookies=self.use_cookies)
        except Exception, e:
            LOG.debug('Error loading url [%s]', url, exc_info=True)
            return ArticleResult(url=url, status=ArticleResult.ERROR, error=e)

        try:
            title = self.extract_title(soup)
            body_html = self.extract_body(soup)
            author = self.extract_author(soup)
        except ScraperException, e:
            LOG.debug(e.message)
            return ArticleResult(url, status=ArticleResult.ERROR, error=e)
        except Exception, e:
            LOG.debug('Error parsing URL [%s]', url, exc_info=True)
            return ArticleResult(url, status=ArticleResult.ERROR, error=e)

        body_text = self.html2text.handle(body_html).strip()

        if existing_article:
            article = existing_article
            status = ArticleResult.EXISTS
        else:
            article = Article(url=url, news_source=self.news_source, relevant=True)
            status = ArticleResult.CREATED

        article.orig_html = body_html
        article.bodytext = body_text
        article.title = title
        article.author = author

        return ArticleResult(url=url, status=status, article=article)

    def extract_title(self, soup):
        title = ''

        if self.title_selector:
            title_tags = soup.select(self.title_selector)
            if title_tags and len(title_tags) > 0:
                title = title_tags[0].get_text(strip=True)
        if not title:
            title = soup.title.get_text(strip=True)
        return title

    def extract_body(self, soup):
        if not self.body_selector:
            raise ScraperException('No body selector!')

        results = soup.select(self.body_selector)
        if len(results) < 1:
            raise ScraperException("Can't find article body '{}'".format(self.body_selector))
        elif len(results) > 1:
            LOG.debug('Multiple article bodies (%d) found for selector: %s. Taking first.',
                      len(results), self.body_selector)

        body_html = results[0]
        if self.exclude_selector:
            remove_elements = body_html.select(self.exclude_selector)
            for element in remove_elements:
                element.extract()

        return body_html.prettify()

    def extract_author(self, soup):
        if self.author_selector:
            results = soup.select(self.author_selector)
            if results and len(results) > 0:
                return results[0].get_text(strip=True)
        return ''
