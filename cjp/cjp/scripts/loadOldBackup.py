#!/usr/bin/env python

import scraper
import re
import datetime
import time

scraper.setPathToDjango(__file__)

from django.db import transaction
import cjp.crimedata.models as models

DATAFILE = '/home/john/old/cpd/dbbackup.txt'

def toDate(unicodeMilliseconds):
    return toDatetime(unicodeMilliseconds).date()
    
def toTime(unicodeMilliseconds):
    return toDatetime(unicodeMilliseconds).time()
    
def toDatetime(unicodeMilliseconds):
    return datetime.datetime(*time.gmtime(int(unicodeMilliseconds)/1000)[:6])

with open(DATAFILE, 'r') as data:
    for line in data:
        if line.startswith('INSERT INTO cpd_crime '):
            fname = None
            fvalue = None
            
            line = line.replace('INSERT INTO cpd_crime ', 'fname=', 1)
            line = line.replace(') VALUES (', ')\n\nfvalue=(', 1)
            line = re.sub(r'((\w+)([,)]))', r"'\2'\3", line, count=31)
            line = re.sub(r'((-?\d+\.\d+)(,))', r"'\2'\3", line, count=31)
            #print line
            exec(line)
            
            rec = dict(zip(fname, fvalue))
            
            rec['web_date'] = toDatetime(rec['orig_dateocc'])
            rec['crime_date'] = toDate(rec['orig_dateocc'])
            rec['crime_time'] = toTime(rec['orig_dateocc'])
            
            report = models.CrimeReport(
                    orig_ward           = rec['orig_ward'],
                    orig_rd             = rec['orig_rd'],
                    orig_beat_num       = rec['orig_beat_num'],
                    orig_location_descr = rec['orig_location_descr'],
                    orig_fbi_descr      = rec['orig_fbi_descr'],
                    orig_domestic_i     = rec['orig_domestic_i'],
                    orig_status         = rec['orig_status'],
                    orig_street         = rec['orig_street'],
                    orig_fbi_cd         = rec['orig_fbi_cd'],
                    orig_dateocc        = rec['orig_dateocc'],
                    orig_stnum          = rec['orig_stnum'],
                    orig_description    = rec['orig_description'],
                    orig_stdir          = rec['orig_stdir'],
                    orig_curr_iucr      = rec['orig_curr_iucr'],
                    
                    web_case_num    = rec['web_case_num'], 
                    web_date        = rec['web_date'],
                    web_block       = rec['web_block'],
                    web_code        = rec['web_code'], 
                    web_crime_type  = rec['web_crime_type'],
                    web_secondary   = rec['web_secondary'],
                    web_arrest      = rec['web_arrest'],
                    web_location    = rec['web_location'],
                    web_domestic    = rec['web_domestic'],
                    web_beat        = rec['web_beat'],
                    web_ward        = rec['web_ward'],
                    web_nibrs       = rec['web_nibrs'],
                    
                    crime_date      = rec['crime_date'],
                    crime_time      = rec['crime_time'],
                    
                    geocode_latitude    = rec['geocode_latitude'],
                    geocode_longitude   = rec['geocode_longitude'],
                    geocode_point       = 'POINT(%s %s)' % (rec['geocode_longitude'], rec['geocode_latitude'])
            )
            report.save()
            #print rec
            #print 'POINT(%s %s)' % (rec['geocode_longitude'], rec['geocode_latitude'])
            #print