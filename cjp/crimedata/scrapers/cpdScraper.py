#!/usr/bin/env python

CONFIGURATION_FILENAME = "cpdScraperConfig.txt"

import datetime
import getopt
import httplib
import scraper
import sys
import os
import pytz
import re
import time
import urllib
import urllib2
import xml.dom.minidom

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() # needed to be sure models are loaded

from django.db import transaction
import crimedata.models as models

L_ERR  = 'E'
L_INFO = 'I'

class CPDScraper(scraper.BasicScraper):
    def __init__(self, configFile, rebuild):
        super(CPDScraper, self).__init__(configFile, models)
        self.__rebuild = rebuild
        self.__logMessages = []

    def logError(self, message):
        super(CPDScraper, self).logError(message)

    def logInfo(self, message):
        super(CPDScraper, self).logInfo(message)

    def addErrorLog(self, message):
        self.__logMessages.append((L_ERR, message))

    def addInfoLog(self, message):
        self.__logMessages.append((L_INFO, message))

    def saveLogs(self):
        for t, m in self.__logMessages:
            if t == L_ERR:
                self.logError(m)
            elif t == L_INFO:
                self.logInfo(m)
        self.__logMessages = []

    def run(self):
        self.logInfo("START CPD GIS Scraper")

        if (self.__rebuild):
            self.__rebuildPast()
        else:
            self.__addLatest()

        # create lookup tables
        with transaction.atomic():
            models.LookupCRCrimeDateMonth.createLookup()
            models.LookupCRCode.createLookup()
            models.LookupCRCrimeType.createLookup()
            models.LookupCRSecondary.createLookup()
            models.LookupCRBeat.createLookup()
            models.LookupCRWard.createLookup()
            models.LookupCRNibrs.createLookup()

        tables = (
            models.CrimeReport,
            models.LookupCRCrimeDateMonth,
            models.LookupCRCode,
            models.LookupCRCrimeType,
            models.LookupCRSecondary,
            models.LookupCRBeat,
            models.LookupCRWard,
            models.LookupCRNibrs)

        for table in tables:
            table.objects.raw('VACUUM %s' % table._meta.db_table)

        self.logInfo("END CPD GIS Scraper")

    def __rebuildPast(self):
        """
        Reloads the data for the available days,
        config's days_available.

        This will replace the data for these days
        in the database.  This is done, because it
        appears that the CPD updates their data,
        so periodically, someone may want to refresh
        the database.
        """
        date = self.__getStartDate(int(self.getConfig('config', 'days_available')))
        oneDayDuration = datetime.timedelta(days = 1)

        for x in range(int(self.getConfig('config', 'days_available'))):
            self.__getDayData(date)
            date = date + oneDayDuration
            time.sleep(int(self.getConfig('config', 'seconds_between_queries')))

    def __addLatest(self):
        """
        Reloads a few days to catch updates
        """
        date = self.__getStartDate(int(self.getConfig('config', 'days_update')))
        self.addInfoLog("addLatest() for %s" % date)

        # find all dates currently in the database
        # lastDateStr = self.__getDateString(date)

        # cursor = conn.cursor()

        # cursor.execute("""select distinct(to_char(crime_date, 'YYYY-MM-DD')) as the_date
        #                  from cpd_crime where crime_date >= date(%s)""", [lastDateStr])

        # build a hash of the current dates in db
        #existingDates = set()
        #for row in cursor:
        #   existingDates.add(row[0])

        oneDayDuration = datetime.timedelta(days = 1)

        # for any date not in the database, go request
        # the data from the server
        for x in range(int(self.getConfig('config', 'days_update'))):
            self.__getDayData(date)

            time.sleep(int(self.getConfig('config', 'seconds_between_queries')))

            date = date + oneDayDuration;

    def __getStartDate(self, dateLimit):
        """
        Determines how far back to go to retrieve data from the CPD website.

        Returns a datetime object representing the earliest date to process.
        """
        now = datetime.datetime.now(pytz.timezone('US/Central'))
        date = now.date()
        backDays = (int(self.getConfig('config', 'days_backdated')) + dateLimit)
        duration= datetime.timedelta(days = backDays)
        return date - duration


    def __getDayData(self, searchDate):
        #with transaction.commit_manually(): # commented just to get this working with Django 1.8
            print "DAY:", searchDate
            self.addInfoLog("START DAY %s" % searchDate)
            self.addInfoLog("Removing any previous data for date %s" % searchDate)

            # remove old versions of data of they exist
            # NOTE: not really removed until commit() is called
            # cursor.execute("DELETE FROM cpd_crime where crime_date = date(%s)", [dateStr])
            models.CrimeReport.objects.filter(crime_date=searchDate).delete()

            # number of records to request each time
            featureLimit = int(self.getConfig('config', 'num_records_request'))

            # record id to start with; for paging results from webserver
            beginRecord = 1

            # flag to signal processing should stop
            done = False

            # total count of records added
            totalRecordsAdded = 0

            # flag signalling if some error occured
            error = False

            # flag signalling there is more data to get; send another request
            hasMore = False

            # number of records saved in db from last request
            inserted = 0

            while not done:
                # build and ARCXML query and send it
                req = self.__buildRequestPost(searchDate, featureLimit, beginRecord);

                self.addInfoLog("Querying...")

                # if we recieve a good response, process it. Otherwise,
                # stop and cancel the database transaction for this day
                try:
                    response = urllib2.urlopen(req)
                    content = response.read()

                    # try to parse the ARCXML and insert data into the db
                    error, hasMore, inserted = self.__parseResponse(content)

                    # if any error is returned from processing the XML,
                    # stop and cancel the database transaction for this day
                    if error:
                        done = True
                    else:
                        totalRecordsAdded += inserted;
                        self.addInfoLog("Inserted %d records" % inserted)

                        # See if there are more records to get, or
                        # if we are done
                        if hasMore:
                            beginRecord += featureLimit
                            time.sleep(int(self.getConfig('config', 'seconds_between_queries')))
                        else:
                            done = True
                except urllib2.URLError, e:
                    self.addErrorLog("Bad response from server, URLError: %s" % e)
                    done = True
                    error = True
                except httplib.BadStatusLine, e:
                    self.addErrorLog("Bad response from server, BadStatusLine: %s" % e)
                    done = True
                    error = True


            # if there is an error, or no data inserted, rollback the
            # transaction and preserve whatever was there.  This is a
            # safety feature.
            #
            # Otherwise, commit and save the new data
            if error:
                transaction.rollback()
                self.addErrorLog("Error occurred. No change to database for date %s" % searchDate)
            elif inserted == 0:
                transaction.rollback()
                self.addInfoLog("No records inserted, retaining old data. No change to database for date %s" % searchDate)
            else:
                transaction.commit()
                self.addInfoLog("Added %d records to table for date %s" % (totalRecordsAdded, searchDate))

            # Just save the logs
            self.saveLogs()
            transaction.commit()


    def __buildRequestPost(self,
                            searchDate,     # day to search
                            featureLimit,   # max number of features (crimes)
                                            # in one query
                            beginRecord     # which record to start features at,
                                            # this is what pages through the
                                            # results.
                          ):
        # the range for a search is 24 hours of one day
        startTime = "%d-%02d-%02d 00:00:00" % (
            searchDate.year, searchDate.month, searchDate.day)

        endTime = "%d-%02d-%02d 23:59:59" % (
            searchDate.year, searchDate.month, searchDate.day)

        url = 'http://gis.chicagopolice.org/servlet/com.esri.esrimap.Esrimap?ServiceName=clearMap&CustomService=Query&ClientVersion=4.0&Form=True&Encode=False'

        data = {'JavaScriptFunction' : "parent.MapFrame.processXML",
                'BgColor'            : "#000000",
                'FormCharset'        : "ISO-8859-1",
                'RedirectURL'        :  "",
                'HeaderFile'         :  "",
                'FooterFile'         :  "",
                'ArcXMLRequest'      :  '''<?xml version="1.0" encoding="UTF-8" ?>
                                <ARCXML VERSION="1.1">
                                 <REQUEST>
                                  <GET_FEATURES outputmode="xml" geometry="true" globalenvelope="true" envelope="true"
                                                checkesc="true" compact="true" beginrecord="%(beginRecord)s">
                                   <LAYER id="999" type="featureclass">
                                    <DATASET name="GIS.clearMap_crime_90days" type="point" workspace="sde_ws-1"  />
                                   </LAYER>
                                   <SPATIALQUERY where=" GIS.clearMap_crime_90days.DATEOCC between {ts &apos;%(startTime)s&apos;} AND  {ts &apos;%(endTime)s&apos;} " featurelimit="%(featureLimit)s" subfields="RD DATEOCC STNUM STDIR STREET CURR_IUCR FBI_DESCR DESCRIPTION STATUS LOCATION_DESCR DOMESTIC_I BEAT_NUM WARD FBI_CD #SHAPE# #ID#">
                                        <FILTERCOORDSYS id="4326" />
                                        <FEATURECOORDSYS id="4326" />
                                   </SPATIALQUERY>
                                  </GET_FEATURES>
                                 </REQUEST>
                                </ARCXML>''' % {
                                    'beginRecord' : beginRecord,
                                    'startTime' : startTime,
                                    'endTime' : endTime,
                                    'featureLimit' : featureLimit
                                }

        }

        return urllib2.Request(url, urllib.urlencode(data))

    def __parseResponse(self, data):
        match = re.search(r'(<\?xml.*<\/ARCXML>)', data)
        if match is None:
            self.addErrorLog("Cannot find XML in response")
            return True, False , 0

        xmlData = match.group(0)

        # The parser does not like the #'s so let's alter them to xxx
        xmlData = re.sub('#SHAPE#', 'xxxSHAPExxx', xmlData)

        doc = xml.dom.minidom.parseString(xmlData)

        # There should only be one ARCXML and should be version 1.1
        arcxml = doc.getElementsByTagName('ARCXML')
        if arcxml.length != 1:
            self.addErrorLog("Unexpected XML.  Incorrect number ARCXML tags: %d" % arcxml.length)
            return True, False , 0

        version = arcxml[0].getAttribute('version')
        if version != '1.1':
            self.addErrorLog("Unexpected XML.  Wrong version of ARCXML: %s. Expecting: 1.1" % version)
            return True, False , 0

        # There should only be one RESPONSE
        response = doc.getElementsByTagName('RESPONSE')
        if response.length != 1:
            self.addErrorLog("Unexpected XML.  Incorrect number RESPONSE tags: %d" % response.length)
            return True, False , 0

        # There should be only one FEATURES
        features = response[0].getElementsByTagName('FEATURES')
        if features.length != 1:
            self.addErrorLog("Unexpected XML.  Incorrect number FEATURES tags: %d" % features.length)
            return True, False , 0

        # There should be only one FEATURECOUNT
        featureCounts = features[0].getElementsByTagName('FEATURECOUNT')
        if featureCounts.length != 1:
            self.addErrorLog("Unexpected XML.  Incorrect number FEATURECOUNT tags: %d" % featureCounts.length)
            return True, False , 0

        # count is the number of feautures, or crimes, in the response
        count  = int(featureCounts[0].getAttribute("count"))

        # hasMore is a boolean string "true" or "false" which, if
        # "true", means that there are more records available
        hasMore = featureCounts[0].getAttribute("hasmore")

        # lead string used in XML repsonse for attribures in a field
        # For example, there should be an attribute
        #       GIS.clearMap_crime_90days.RD
        LEAD = 'GIS.clearMap_crime_90days';
        FIELD_ATTRIBUTES = ( 'RD', 'DATEOCC', 'STNUM', 'STDIR', 'STREET',
                            'CURR_IUCR', 'FBI_DESCR', 'DESCRIPTION', 'STATUS',
                            'LOCATION_DESCR', 'DOMESTIC_I', 'BEAT_NUM',
                            'WARD', 'FBI_CD')

        # total number of records inserted from this respone
        insertCount = 0

        # Process each FEATURE
        for feature in features[0].getElementsByTagName('FEATURE'):
            rec = {}
            for tag in feature.childNodes:
                if tag.nodeName == 'FIELDS':
                    for attr in FIELD_ATTRIBUTES:
                        val = tag.getAttribute("%s.%s" % (LEAD, attr))

                        if not val:
                            self.addErrorLog("Missing ATTRIBUTE %s.%s" % (LEAD, attr))
                            if attr in ("LOCATION_DESCR", "FBI_CD"):
                                rec[attr] = "MISSING"
                            elif attr == "DESCRIPTION":
                                rec[attr] = "NO DESCRIPTION"
                            elif attr in ("STDIR", "CURR_IUCR"):
                                rec[attr] = "-"
                            elif attr in ("WARD", "STNUM", "BEAT_NUM"):
                                rec[attr] = "0"
                        else:
                            rec[attr] = val.upper()

            ## setup a formatter to translate the datetime
            ## values in the XML response to strings for the database

            ## create strings for the date fields
            rec['WEB_DATE'] = self.toDatetime(rec['DATEOCC'])
            rec['CRIME_DATE'] = self.toDate(rec['DATEOCC'])
            rec['CRIME_TIME'] = self.toTime(rec['DATEOCC'])

            # create the block address from the real address elements
            rec['WEB_BLOCK'] = "%d %s %s" % (
                (int(rec['STNUM'])  - (int(rec['STNUM'])  % 100)),
                rec['STDIR'], rec['STREET']
            )

            # FBI_DESCR may be missing (?)
            if 'FBI_DESCR' not in rec.keys():
                rec['FBI_DESCR'] = ''

            # the string "(INDEX)" is removed when showing the crime type
            rec['WEB_CRIME_TYPE'] = rec['FBI_DESCR']
            rec['WEB_CRIME_TYPE'] = re.sub(r' *\([Ii][Nn][Dd][Ee][Xx]\) *$', '', rec['WEB_CRIME_TYPE'] )

            # create the boolean arrest from the status
            if re.search(r'^3', rec['STATUS']):
                rec['WEB_ARREST'] = 'Y'
            else:
                rec['WEB_ARREST'] = 'N'

            # extract the latitude and longitude of the crime
            envelopes = feature.getElementsByTagName('ENVELOPE')
            if envelopes.length != 1:
                self.addErrorLog("Unexpected XML.  Incorrect number ENVELOPE tags: %d" % envelopes.length)
                return True, False, 0

            # I think these are the lat long, if not try MULTIPOINTS later
            rec['LONGITUDE'] = envelopes[0].getAttribute('minx')
            rec['LATITUDE'] = envelopes[0].getAttribute('miny')

            #print rec

            report = self.model.CrimeReport(
                    orig_ward           = rec['WARD'],
                    orig_rd             = rec['RD'],
                    orig_beat_num       = rec['BEAT_NUM'],
                    orig_location_descr = rec['LOCATION_DESCR'],
                    orig_fbi_descr      = rec['FBI_DESCR'],
                    orig_domestic_i     = rec['DOMESTIC_I'],
                    orig_status         = rec['STATUS'],
                    orig_street         = rec['STREET'],
                    orig_fbi_cd         = rec['FBI_CD'],
                    orig_dateocc        = rec['DATEOCC'],
                    orig_stnum          = rec['STNUM'],
                    orig_description    = rec['DESCRIPTION'],
                    orig_stdir          = rec['STDIR'],
                    orig_curr_iucr      = rec['CURR_IUCR'],

                    web_case_num    = rec['RD'],
                    web_date        = rec['WEB_DATE'],
                    web_block       = rec['WEB_BLOCK'],
                    web_code        = rec['CURR_IUCR'],
                    web_crime_type  = rec['WEB_CRIME_TYPE'],
                    web_secondary   = rec['DESCRIPTION'],
                    web_arrest      = rec['WEB_ARREST'],
                    web_location    = rec['LOCATION_DESCR'],
                    web_domestic    = rec['DOMESTIC_I'],
                    web_beat        = rec['BEAT_NUM'],
                    web_ward        = rec['WARD'],
                    web_nibrs       = rec['FBI_CD'],

                    crime_date      = rec['CRIME_DATE'],
                    crime_time      = rec['CRIME_TIME'],

                    geocode_latitude    = rec['LATITUDE'],
                    geocode_longitude   = rec['LONGITUDE'],
                    geocode_point       = 'POINT(%s %s)' % (rec['LONGITUDE'], rec['LATITUDE'])
            )
            report.save()

            insertCount += 1

        if insertCount != count:
            self.addErrorLog("Inserted %d records into DB, but XML reported %d" %(insertCount, count))

        return False, hasMore == "true", insertCount

    def toDate(self, unicodeMilliseconds):
        return self.toDatetime(unicodeMilliseconds).date()

    def toTime(self, unicodeMilliseconds):
        return self.toDatetime(unicodeMilliseconds).time()

    def toDatetime(self, unicodeMilliseconds):
        return datetime.datetime(*time.gmtime(int(unicodeMilliseconds)/1000)[:6])

def printUsage(exitValue):
    """
    cpdScraper.py - scrapes the CPD GIS website

    USAGE

    cpdScraper.py --rebuild

    DESCRIPTION

    --rebuild
    Downloads the last 90 days of crime data.  If data is already in
    the database, it is replaced.
    """

    for line in printUsage.__doc__.expandtabs().splitlines():
        print line.lstrip()
    sys.exit(exitValue)

def main(rebuild=False):
    configurationLocation = os.path.dirname(__file__)
    configPath = os.path.join(configurationLocation, CONFIGURATION_FILENAME)
    scraper = CPDScraper(configPath, rebuild)
    scraper.run()

if __name__ == '__main__':
    rebuild = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["rebuild"])
    except getopt.GetoptError, err:
        print str(err)
        printUsage(2)

    for option, argument in opts:
        if option == "--rebuild":
            rebuild=True
        else:
            assert False, "unhandled command line option: " + option

    main(rebuild)
