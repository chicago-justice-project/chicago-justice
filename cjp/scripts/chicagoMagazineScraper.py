#!/usr/bin/env python

CONFIGURATION_FILENAME = "chicagoMagazineScraperConfig.txt"

from BeautifulSoup import BeautifulSoup, Comment
import feedparser
import httplib
import scraper
import sys
import os
import re
import time
import urllib2

scraper.setPathToDjango(__file__)

from django.db import transaction
import cjp.newsarticles.models as models

class ChicagoMagazineScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(ChicagoMagazineScraper, self).__init__(models.FEED_CHICAGOMAGAZINE,
                                             configFile, models)
        
    def run(self):
        self.logInfo("START Chicago Magazine Feed Scraper")
        
        feedUrls = self.getConfig('config', 'feed_url').split('\n')
        
        for feedUrl in feedUrls:
            self.processFeed(feedUrl)
            
        self.logInfo("END Chicago Magazine Feed Scraper")
        
    def processFeed(self, feedUrl):
        feed = feedparser.parse(feedUrl)

        if 'channel' not in feed:
            self.logError("Expected channel missing in RSS Feed")
            return
        
        channel = feed['channel']
        if 'title' not in channel.keys() :
            self.logError("Channel title missing. URL = %s" % feedUrl)
            return

        if 'links' not in channel.keys():
            self.logError("Expected channel link missing")
            return
        else:
            found=False
            for link in channel['links']:
                if link['href'].startswith('http://www.chicagomag.com/Chicago-Magazine/'):
                    found=True
            if not found:
                self.logError("Expected channel link missing")
                return

        if len(feed.entries) == 0:
            self.logError("No entries in RSS feed")
            return
        
        insertCount = 0
        
        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))

        for item in feed.entries:
            if len(item.link) == 0:
                self.logError("Item link is empty, skipping entry : %s" % item)
                continue
            
            cnt = self.processItem(item.link)
            insertCount += cnt

            time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Chicago Magazine articles" % insertCount)
    
    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)
        content = re.sub(re.compile(r"\r",  flags=re.MULTILINE), " ", content)

        title = re.search(r"<title>(.*)</title>", content)
        if title == None:
            title = "Missing"
        else:
            title = title.group(1)

        content = self.cleanScripts(content)

        soup = BeautifulSoup(content)
        unneededText = (('div', 'commentsform'),
            )
        for tagName, className in unneededText:
            results = soup.findAll(tagName, { "class" : className })
            [result.extract() for result in results]
            
        results = soup.findAll("div", { "id" : "article" })
        
        if len(results) != 1:
            raise scraper.FeedException('Number of div class="body" in HTML is not 1. Count = %d' % len(results))
        
        self.saveStory(url, title, content, results[0])
            

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = ChicagoMagazineScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
