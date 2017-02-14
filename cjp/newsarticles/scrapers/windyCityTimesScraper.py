#!/usr/bin/env python

CONFIGURATION_FILENAME = "windyCityTimesScraperConfig.txt"

from bs4 import BeautifulSoup, Comment
import feedparser
import httplib
import scraper
import sys
import os
import re
import time
import urllib2
from cookielib import CookieJar

from django.db import transaction
import newsarticles.models as models

class WindyCityTimesScraper(scraper.FeedScraper):
    def __init__(self, configFile):
        super(WindyCityTimesScraper, self).__init__(models.FEED_WINDYCITYTIMES,
                                             configFile, models)
        
    def run(self):
        """ NOT an RSS feed. Just an HTML Page """
        self.logInfo("START Windy City Times Feed Scraper")
        
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
        
        self.logInfo("END Windy City Times Feed Scraper")
        
    def processFeed(self, feedUrl, mainContent):
        
        insertCount = 0
        
        sleepTime = int(self.getConfig('config', 'seconds_between_queries'))
        
        mainContent = self.cleanScripts(mainContent)
        
        soup = BeautifulSoup(mainContent, 'html.parser')
        
        results = soup.findAll("a", { "class" : 'page-c-head' })
        
        processedLinks = set()
        
        for tag in results:
            link = tag['href']
            if link in processedLinks: continue
            processedLinks.add(link)
            
            cnt = self.processItem(link, headers=[('User-agent', 'Mozilla/5.0')])
            insertCount += cnt
            
            # they have a long list that does back many days
            # limit number of downloads
            if insertCount == 40: break

            time.sleep(sleepTime)

        self.logInfo("Inserted/updated %d Windy City Times articles" % insertCount)
    
    def parseResponse(self, url, content):
        content = content.strip()
        content = re.sub(re.compile(r"^\s+$",  flags=re.MULTILINE), "", content)
        content = re.sub(re.compile(r"&copy;$",  flags=re.MULTILINE), " ", content)
        
        content = self.cleanScripts(content)
        
        # They don't know the difference between span and div
        # Their spans need to be converted for the soup to work
        content = re.sub("<span ", "<div ", content)
        content = re.sub("</span>", "</div>", content)
        
        soup = BeautifulSoup(content, 'html.parser')
        
        def t(v):
            print "=====", v
            return True
        
        results = soup.findAll("div", { "class" : "article-body" })
        
        if len(results) == 0:
            raise scraper.FeedException('Number of tables in HTML is not 1. Count = %d' % len(results))
        
        resultHTML = ""
        for r in results:
            resultHTML += "<div>%s</div>" % str(r)
            
        resultHTML = "".join(i for i in resultHTML if ord(i)<128)
        
        titleResults = soup.findAll("div", { "class" : "fp-newshead" })

        if len(titleResults) != 1:
            title = "Missing"
        else:
            title = str(titleResults[0].contents[0])
            title = re.sub(r'<[^>]{1,}>', '', title)
            
        self.saveStory(url, title, content, resultHTML)

def main():
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = WindyCityTimesScraper(configPath)
    scraper.run() 

if __name__ == '__main__':
    main()
