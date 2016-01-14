#!/usr/bin/env python

CONFIGURATION_FILENAME = "chicagoReporterScraperConfig.txt"

from BeautifulSoup import BeautifulSoup, Comment
import feedparser
import httplib
import html2text
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

class ChicagoReporterScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(ChicagoReporterScraper, self).__init__(models.FEED_CHICAGOREPORTER,
                                             configFile, models)
        
    def run(self):
        self.logInfo("START Chicago Reporter Feed Scraper")
        
        feedUrls = self.getConfig('config', 'feed_url').split('\n')

        for feedUrl in feedUrls:
            self.processFeed(feedUrl)
        
        self.logInfo("END Chicago Reporter Feed Scraper")
    
    def processFeed(self, feedUrl):
        
        urlParts = urlparse(feedUrl)
        baseUrl = "%s://%s" % (urlParts[0], urlParts[1])
        
        try:
            response = urllib2.urlopen(feedUrl)
            html = response.read()
        except Exception, e:
            self.logError("Error downloading Feed URL Page: %s" % e)
            return

        insertCount = 0
        
        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))
        
        html = self.cleanScripts(html)
        
        soup = BeautifulSoup(html)
        
        results = soup.findAll("div", { "class" : lambda val: val != None and "views-field-view-node" in val})

        for result in results:
            anchor = result.findAll('a')
            if len(anchor) != 1:
                self.logError("Error extracting anchor.  Count expect is 1, result was %s" % len(anchor))
                continue
            link = "%s%s" % (baseUrl, anchor[0]['href'])

            cnt = self.processItem(link)
            insertCount += cnt

            time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Chicago Reporter articles" % (insertCount,))       
    
    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)

        title = re.search(r"<title>(.*)</title>", content)
        if title == None:
            title = "Missing"
        else:
            title = title.group(1)
            
        content = self.cleanScripts(content)            

        soup = BeautifulSoup(content)
        results = soup.findAll("div", {'class' : lambda val: val != None and re.search(r"\bcol-center\b", val)})
        
        if len(results) != 1:
            raise scraper.FeedException('Number of story-body ids in HTML is not 1. Count = %d URL = %s' % (len(results), url))
            
        self.saveStory(url, title, content, results[0])
            

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = ChicagoReporterScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
