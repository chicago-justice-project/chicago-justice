#!/usr/bin/env python

CONFIGURATION_FILENAME = "wttwScraperConfig.txt"

from bs4 import BeautifulSoup, Comment
import feedparser
import httplib
import sys
import os
import re
import time
import urllib2
import scraper

from django.db import transaction
import newsarticles.models as models

class WTTWScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(WTTWScraper, self).__init__(models.FEED_WTTW,
                                             configFile, models)
        
    def run(self):
        self.logInfo("START WTTW Feed Scraper")
        
        feedUrl = self.getConfig('config', 'feed_url')
        feed = feedparser.parse(feedUrl)

        if 'channel' not in feed:
            self.logError("Expected channel missing in RSS Feed")
            return
        
        channel = feed['channel']

        if 'link' not in channel.keys() or channel['link'] != 'http://chicagotonight.wttw.com':
            self.logError("Expected channel link missing")
            return

        if len(feed.entries) == 0:
            self.logError("No entries in RSS feed")
            return
        
        self.processFeed(feed)
        
        self.logInfo("END WTTW Feed Scraper")
        
    def processFeed(self, feed):
        insertCount = 0
        
        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))

        for item in feed.entries:
            if 'feedburner_origlink' not in item.keys() or len(item.feedburner_origlink) == 0:
                self.logError("item guid is empty, skipping")
                continue
            cnt = self.processItem(item.feedburner_origlink)
            insertCount += cnt
            time.sleep(sleepTime)
        self.logInfo("Inserted/updated %d WTTW articles" % insertCount)
    
    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)
        title = re.search(r"<title>(.*)</title>", content)
        if title == None:
            title = "Missing"
        else:
            title = title.group(1)
        content = self.cleanScripts(content)            
        soup = BeautifulSoup(content, 'html.parser')
        results = soup.findAll('div', { 'class': 'main-container' })
        if len(results) != 1:
            raise scraper.FeedException('Number of story-body ids in HTML is not 1. Count = %d URL = %s' % (len(results), url))
        self.saveStory(url, title, content, results[0])
            

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = WTTWScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
