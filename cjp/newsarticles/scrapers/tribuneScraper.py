#!/usr/bin/env python

CONFIGURATION_FILENAME = "tribuneScraperConfig.txt"

from bs4 import BeautifulSoup, Comment
import feedparser
import httplib
import html2text
import scraper
import sys
import os
import re
import time
import urllib2

from django.db import transaction
import newsarticles.models as models

class TribuneScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(TribuneScraper, self).__init__(models.FEED_TRIBUNE,
                                             configFile, models)
        
    def run(self):
        self.logInfo("START Tribune Feed Scraper")
        
        feedUrls = self.getConfig('config', 'feed_url').split('\n')

        for feedUrl in feedUrls:
            self.processFeed(feedUrl)
        
        self.logInfo("END Tribune Feed Scraper")
    
    def processFeed(self, feedUrl):
        feed = feedparser.parse(feedUrl)

        if 'channel' not in feed:
            self.logError("Expected channel title missing. URL = %s" % feedUrl)
            return

        channel = feed['channel']
        
        if 'title' not in channel.keys() :
            self.logError("Channel title missing. URL = %s" % feedUrl)
            return

        if 'link' not in channel.keys() or not channel['link'].startswith('http://www.chicagotribune.com/'):
            self.logError("Expected channel link missing. URL = %s" % feedUrl)
            return

        if len(feed.entries) == 0:
            self.logError("No entries in RSS feed. URL = %s" % feedUrl)
            return

        insertCount = 0
        
        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))

        for item in feed.entries:
            if 'link' not in item.keys() or len(item.link) == 0:
                self.logError("item link is empty, skipping. Feed URL = %s" % feedUrl)
                continue

            cnt = self.processItem(item.link)
            insertCount += cnt

            time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Tribune articles" % (insertCount,))       
        
    def processItem(self, link):
        if re.search(r'\.photo\?track', link) != None:
                return 0
            
        return super(TribuneScraper, self).processItem(link)
    
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
        results = soup.findAll('div', { 'itemprop': 'articleBody' })
        
        if len(results) != 1:
            raise scraper.FeedException('Number of story-body ids in HTML is not 1. Count = %d URL = %s' % (len(results), url))
            
        self.saveStory(url, title, content, results[0])
            

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = TribuneScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
