# help stuff for scrapers

import abc
import ConfigParser
import exceptions
import html2text
import httplib
import os
import re
import sys
import urllib2
import datetime
from cookielib import CookieJar

class FeedException(exceptions.Exception):
    def __init__(self, info):
        self.__info = info

    def __str__(self):
        return self.__info

class BasicScraper(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, configFile, djangoModel):
        if not os.path.exists(configFile):
            raise IOError("Cannot find configuration file %s" % configFile)
        self.__config = ConfigParser.RawConfigParser()
        self.__config.read(configFile)
        self.__model = djangoModel

    def getConfig(self, section, option):
        return self.__config.get(section, option)

    @property
    def model(self):
        return self.__model

    @abc.abstractmethod
    def logError(self, message):
        """Log an Error"""
        return

    def logError(self, message):
        if self.getConfig('config', 'printLog') == '1':
            ts = datetime.datetime.now().isoformat()
            print("{} ERROR: {}".format(ts, message))

    def logInfo(self, message):
        if self.getConfig('config', 'printLog') == '1':
            ts = datetime.datetime.now().isoformat()
            print("{} INFO: {}".format(ts, message))

class FeedScraper(BasicScraper):
    __metaclass__ = abc.ABCMeta

    def __init__(self, feedName, configFile, djangoModel):
        super(FeedScraper, self).__init__(configFile, djangoModel)
        self.__feedName = feedName

    @abc.abstractmethod
    def run(self):
        """Process the feed"""
        return

    def logError(self, message):
        super(FeedScraper, self).logError(message)

    def logInfo(self, message):
        super(FeedScraper, self).logInfo(message)

    def processItem(self, link, withCookies=False, headers=None):
        self.logInfo("Querying %s" % link)

        # if we recieve a good response, process it. Otherwise,
        # stop and cancel the database transaction for this day

        if withCookies:
            cj = CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
            opener = urllib2.build_opener()
        if headers is not None:
            opener.addheaders = headers
        try:
            response = opener.open(link)
            content = response.read()
            self.parseResponse(link, content)
            return 1
        except urllib2.URLError, e:
            self.logError("Bad response from server, URLError: %s" % e)
        except httplib.BadStatusLine, e:
            self.logError("Bad response from server, BadStatusLine: %s" % e)
        except FeedException, e:
            self.logError("Unexpected HTML, FeedException: %s" % e)
        return 0

    @abc.abstractmethod
    def parseResponse(self, url, content):
        """Setup process the response.  Should call saveStory when ready"""
        return

    def cleanScripts(self, content):
        # non-greedy on script and meta
        content = re.sub(re.compile(r"<\s*script.*?</\s*script\s*>",  flags=re.DOTALL), "", content)
        content = re.sub(re.compile(r"<\s*noscript.*?</\s*noscript\s*>",  flags=re.DOTALL), "", content)
        content = re.sub(re.compile(r"<\s*meta.*?/>",  flags=re.DOTALL), "", content)
        return content

    def saveStory(self, url, title, orig_html, storyHTML):
        if 'prettify' in dir(storyHTML):
            try:
                storyHTML = storyHTML.prettify().decode('utf8')
            except UnicodeEncodeError:
                """Not sure we should be decoding utf8 anyway. BeautifulSoup should be detecting the
                encoding. Leaving the decode for safety and adding this error check for non-UTF8
                pages."""
                storyHTML = storyHTML.prettify()
        #fix for non-utf8 characters.  Won't go in DB otherwise
        # Since just for debugging purposes, don't have to save text if this fails
        try:
            orig_html = "".join(i for i in orig_html if ord(i) < 128)
        except:
            orig_html = "HTML has bad encoding. Cannot save"

        extractedHTML = "\n".join(("""<html><head>
                                        <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
                                        <title>EXTRACTED</title></head><body>""",
                                        storyHTML,
                                        "</body></html>"))

        storyText = html2text.html2text(extractedHTML)
        lines = storyText.splitlines()
        modifiedLines = []
        MAX_LINE_LENGTH = 80
        for line in lines:
            if len(line) > MAX_LINE_LENGTH:
                splitLines = [line[i:i+MAX_LINE_LENGTH]
                              for i in range(0, len(line), MAX_LINE_LENGTH)]
                for sl in splitLines:
                    modifiedLines.append(sl)
            else:
                modifiedLines.append(line)
        storyText = "\n".join(modifiedLines)
        try:
            article = self.model.Article.objects.get(url=url,
                                                     feedname=self.__feedName)
            article.orig_html = orig_html
            article.title = title
            article.bodytext = storyText
            #print "update"
        except self.model.Article.DoesNotExist, e:
            article = self.model.Article(feedname=self.__feedName,
                                         url=url,
                                         orig_html=orig_html,
                                         title=title,
                                         bodytext=storyText,
                                         relevant=True)
            #print "save"
        article.save()

