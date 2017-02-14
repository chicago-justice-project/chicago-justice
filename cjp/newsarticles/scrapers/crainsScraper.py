#!/usr/bin/env python

CONFIGURATION_FILENAME = "crainsScraperConfig.txt"

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

class CrainsScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(CrainsScraper, self).__init__(models.FEED_CRAINS,
                                             configFile, models)
        
    def run(self):
        self.logInfo("START Crains Feed Scraper")
        
        feedUrl = self.getConfig('config', 'feed_url')
        feed = feedparser.parse(feedUrl)

        if 'channel' not in feed: 
            self.logError("Expected channel missing in RSS Feed")
            return
        
        channel = feed['channel']
        if 'title' not in channel.keys() or channel['title'] != 'Chicago Business News':
            self.logError("Expected channel title missing")
            return

        if 'link' not in channel.keys() or channel['link'] != 'http://www.chicagobusiness.com/':
            self.logError("Expected channel link missing")
            return

        if len(feed.entries) == 0:
            self.logError("No entries in RSS feed")
            return
        
        self.processFeed(feed)
        
        self.logInfo("END Crains Feed Scraper")
        
    def processFeed(self, feed):
        insertCount = 0
        
        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))

        for item in feed.entries:
            if len(item.link) == 0:
                self.logError("Item link is empty, skipping entry : %s" % item)
                continue
            
            cnt = self.processItem(item.link, withCookies=True)
            insertCount += cnt

            time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Crains articles" % insertCount)
    
    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)

        title = re.search(r"<title>(.*)\n?</title>", content)
        if title == None:
            title = "Missing"
        else:
            title = title.group(1)
            
        content = self.cleanScripts(content)

        soup = BeautifulSoup(content, 'html.parser')
        unneededText = (
            ('div', 'articleSocialBar'),
            ('div', 'pluck'),
            )
        for tagName, className in unneededText:
            results = soup.findAll(tagName, { "id" : className })
            [result.extract() for result in results]
        
            
        results = soup.findAll('div', { "data-swiftype-name" : 'body' })
        
        if len(results) != 1:
            raise scraper.FeedException('Number of primary-content ids in HTML is not 1. Count = %d' % len(results))
            
        self.saveStory(url, title, content, results[0])
            

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = CrainsScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
