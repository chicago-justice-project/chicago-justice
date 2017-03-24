#!/usr/bin/env python

CONFIGURATION_FILENAME = "dailyHeraldScraperConfig.txt"

from bs4 import BeautifulSoup, Comment
import feedparser
import httplib
import scraper
import sys
import os
import re
import time
import urllib2

from django.db import transaction
import newsarticles.models as models

class DailyHeraldScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(DailyHeraldScraper, self).__init__(models.FEED_DAILYHERALD,
                                                 configFile, models)

    def run(self):
        self.logInfo("START Daily Herald Scraper")

        feedUrl = self.getConfig('config', 'feed_url')
        feed = feedparser.parse(feedUrl)

        if 'channel' not in feed:
            self.logError("Expected channel missing in RSS Feed")
            return

        channel = feed['channel']
        if 'title' not in channel.keys() or 'DailyHerald.com' not in channel['title']:
            self.logError("Expected channel title missing")
            return

        if 'link' not in channel.keys() or channel['link'] != 'http://www.dailyherald.com/news/chicago/':
            self.logError("Expected channel link missing")
            return

        if len(feed.entries) == 0:
            self.logError("No entries in RSS feed")
            return

        self.processFeed(feed)

        self.logInfo("END Daily Herald Scraper")

    def processFeed(self, feed):
        insertCount = 0

        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))

        for item in feed.entries:
            if len(item.guid) == 0:
                self.logError("Item guid is empty, skipping entry : %s" % item)
                continue

            if len(item.link) == 0:
                self.logError("Item link is empty, skipping entry : %s" % item)
                continue

            cnt = self.processItem(item.link)
            insertCount += cnt

            time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Daily Herald articles" % insertCount)

    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)
        content = re.sub(re.compile(r"\r",  flags=re.MULTILINE), " ", content)

        title = re.search(r"<title>(.*)</title>", content)
        if title is None:
            title = "Missing"
        else:
            title = title.group(1)

        content = self.cleanScripts(content)

        soup = BeautifulSoup(content, 'html.parser')
        results = soup.findAll('div', {'class': 'articleText'})

        if len(results) != 1:
            raise scraper.FeedException('Number of primary-content ids in HTML is not 1. Count = %d' % len(results))

        self.saveStory(url, title, content, results[0])


def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = DailyHeraldScraper(configPath)
    scraper.run()

if __name__ == '__main__':
    main()
