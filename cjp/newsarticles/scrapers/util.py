import urlparse
import urllib2
from cookielib import CookieJar
import feedparser
from bs4 import BeautifulSoup

def get_rss_articles(url):
    feed = feedparser.parse(url)
    return feed.entries

def get_rss_links(url):
    feed = feedparser.parse(url)
    links = []
    for item in feed.entries:
        links.append(item.link)
    return links

def get_html_links(url, link_selector):
    soup = load_html(url)
    results = soup.select(link_selector)

    parsed_url = urlparse.urlparse(url, 'http')
    base_url = '{}://{}'.format(parsed_url.scheme, parsed_url.netloc)

    links = set()
    for tag in results:
        link = tag['href']
        if not link:
            continue
        if link.startswith('/'):
            link = base_url + link
        links.add(link)

    return links

def load_html(url, with_cookies=False, headers=None):
    """Attempts to load an HTML page, returning a BeautifulSoup instance. Raises
    any networking or parsing exceptions"""
    if with_cookies:
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    else:
        opener = urllib2.build_opener()

    if headers:
        opener.addheaders = headers

    urlstr = url.encode('utf-8')
    response = opener.open(urlstr)
    html = response.read().decode('utf-8', errors='replace')

    soup = BeautifulSoup(html, 'html.parser')
    return soup
