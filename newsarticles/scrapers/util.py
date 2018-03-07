try: # Try loading Python 3 modules, except to Python 2 modules
    from urllib.parse import urlparse
    from urllib import request as urlopen
except ImportError:
    from urlparse import urlparse
    import urllib2 as urlopen

try: # Try loading Python 3 modules, except to Python 2 modules
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

import feedparser
from bs4 import BeautifulSoup

def get_rss_articles(url):
    feed = feedparser.parse(url)
    return feed.entries

def get_rss_links(url, link_selector):
    feed = feedparser.parse(url)
    links = []
    for item in feed.entries:
        link = item.get(link_selector)
        if link:
            links.append(link)
    return links

def parse_html_links(soup, url, link_selector):
    results = soup.select(link_selector)

    parsed_url = urlparse(url, 'http')
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

def load_html(url, with_cookies=False, headers={}):
    """Attempts to load an HTML page, returning a BeautifulSoup instance. Raises
    any networking or parsing exceptions"""
    if with_cookies:
        cj = CookieJar()
        opener = urlopen.build_opener(urlopen.HTTPCookieProcessor(cj))
    else:
        opener = urlopen.build_opener()

    request = urlopen.Request(url, headers=headers)

    response = opener.open(request)
    html = response.read().decode('utf-8', errors='replace')

    soup = BeautifulSoup(html, 'html.parser')
    return soup
