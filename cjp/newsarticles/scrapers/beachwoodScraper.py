#!/usr/bin/env python

CONFIGURATION_FILENAME = "beachwoodScraperConfig.txt"

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

class BeachwoodScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(BeachwoodScraper, self).__init__(models.FEED_BEACHWOOD,
                                               configFile, models)
        
    def run(self):
        self.logInfo("START Beachwood Reporter Feed Scraper")
        
        feedUrl = self.getConfig('config', 'feed_url')
        feed = feedparser.parse(feedUrl)

        if 'channel' not in feed:
            self.logError("Expected channel missing in Feed")
            return
        
        channel = feed['channel']
        if 'title' not in channel.keys() or channel['title'] != 'Beachwood Reporter':
            self.logError("Expected channel title missing")
            return

        if 'link' not in channel.keys() or channel['link'] != 'http://www.beachwoodreporter.com/':
            self.logError("Expected channel link missing")
            return

        if len(feed.entries) == 0:
            self.logError("No entries in RSS feed")
            return
        
        self.processFeed(feed)
        
        self.logInfo("END Beachwood Reporter Feed Scraper")
        
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
            
            html = item.content[0]['value']
            
            self.saveStory(item.link, item.title, html, html)
            
            insertCount += 1


            time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Beachwood Reporter articles" % insertCount)
    
    def parseResponse(self, url, content):
        """ Not called because text is contained in the URL feed."""
        pass
            

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = BeachwoodScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
