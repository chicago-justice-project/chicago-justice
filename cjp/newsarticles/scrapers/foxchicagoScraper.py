#!/usr/bin/env python

CONFIGURATION_FILENAME = "foxchicagoScraperConfig.txt"

from bs4 import BeautifulSoup, Comment
import feedparser
import httplib
import scraper
import sys
import os
import re
import time
import urllib2
import urlparse
from cookielib import CookieJar

from django.db import transaction
import newsarticles.models as models

class FoxChicagoScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(FoxChicagoScraper, self).__init__(models.FEED_FOX,
                                                configFile, models)

    def run(self):
        """ NOT an RSS feed. Just an HTML Page """
        self.logInfo("START Fox Chicago Feed Scraper")
        feedUrl = self.getConfig('config', 'feed_url')

        try:
            cj = CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            response = opener.open(feedUrl)
            html = response.read()
        except Exception, e:
            self.logError("Error downloading main HTML Page: %s" % e)
            return

        self.processFeed(feedUrl, html)

        self.logInfo("END Fox Chicago Feed Scraper")

    def processFeed(self, feedUrl, mainContent):
        insertCount = 0
        parsedUrl = urlparse.urlparse(feedUrl, 'http')
        baseUrl = '{}://{}'.format(parsedUrl.scheme, parsedUrl.netloc)

        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))

        mainContent = self.cleanScripts(mainContent)

        soup = BeautifulSoup(mainContent, 'html.parser')
        results = soup.findAll("a", {"class": 'story-link'})
        processedLinks = set()

        for tag in results:
            link = tag['href']
            if link.startswith('/'):
                # Handle absolute links without host
                link = baseUrl + link
            if link in processedLinks:
                continue

            processedLinks.add(link)

            cnt = self.processItem(link)
            insertCount += cnt

            #time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Fox Chicago articles" % insertCount)

    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)

        title = re.search(r"<title>(.*)</title>", content)
        if title is None:
            title = "Missing"
        else:
            title = title.group(1)

        content = self.cleanScripts(content)

        soup = BeautifulSoup(content, 'html.parser')
        results = soup.findAll('div', {'class': 'story-content'})

        if len(results) != 1:
            raise scraper.FeedException('Number of primary-content ids in HTML is not 1. Count = %d' % len(results))

        self.saveStory(url, title, content, results[0])


def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = FoxChicagoScraper(configPath)
    scraper.run()

if __name__ == '__main__':
    main()
