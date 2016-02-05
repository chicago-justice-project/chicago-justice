#!/usr/bin/env python

CONFIGURATION_FILENAME = "wlsScraperConfig.txt"

from BeautifulSoup import BeautifulSoup, Comment
import feedparser
import httplib
import scraper
import sys
import os
import re
import time
import urllib2
from urlparse import urlparse

scraper.setPathToDjango(__file__)

from django.db import transaction
import cjp.newsarticles.models as models

class WLSScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(WLSScraper, self).__init__(models.FEED_WLSAM,
                                             configFile, models)
        
    def run(self):
        """ NOT an RSS feed. Just an HTML Page """
        self.logInfo("START WLS Feed Scraper")
        
        feedUrl = self.getConfig('config', 'feed_url')
        
        try:
            response = urllib2.urlopen(feedUrl)
            html = response.read()
        except Exception, e:
            self.logError("Error downloading main HTML Page: %s" % e)
            return
        
        self.processFeed(feedUrl, html)
        
        self.logInfo("END WLS Feed Scraper")
        
    def processFeed(self, feedUrl, mainContent):
        
        urlParts = urlparse(feedUrl)
        baseUrl = "%s://%s" % (urlParts[0], urlParts[1])
        if baseUrl[-1] == '/':
            baseUrl = baseUrl[:-1]
        
        insertCount = 0
        
        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))
        
        soup = BeautifulSoup(mainContent)
        
        results = soup.findAll("div", {"class" : "pagination"})
    
        maxPage = 4
              
        # They use paging      
        for page in range(1, maxPage+1):
            pageUrl = "%s&page=%s" % (feedUrl, page)
            try:
                response = urllib2.urlopen(pageUrl)
                pageHtml = response.read()
                time.sleep(sleepTime)
            except Exception as e:
                self.logError("Error downloading page HTML: %s %s" % (pageUrl, e))
                continue
        
            soup = BeautifulSoup(pageHtml)
            
            results = soup.findAll("a", {"class" : "more"})
    
            for tag in results:
                newUrl = "%s%s" % (baseUrl, tag['href'])
                cnt = self.processItem(newUrl)
                insertCount += cnt
    
                time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d WLS articles" % insertCount)
    
    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)
        content = re.sub(re.compile(r"&copy;$",  flags=re.MULTILINE), " ", content)
        
        content = self.cleanScripts(content)
        
        soup = BeautifulSoup(content)
        
        results = soup.findAll("div", { "id" : "cumulus_content_details" })
        
        if len(results) != 1:
            raise scraper.FeedException('Number of div class="body" in HTML is not 1. Count = %d' % len(results))
        
        title = re.search(r"<title>(.*)</title>", content)
        if title == None:
            title = "Missing"
        else:
            title = title.group(1)
            
        self.saveStory(url, title, content, results[0])

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = WLSScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
