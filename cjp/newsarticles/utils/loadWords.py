#!/usr/bin/env python

import os, sys


def setPathToDjango(scriptFile):
    '''get top-level of Django app'''
    scriptPath = os.path.realpath(scriptFile)
    scriptDir = os.path.dirname(scriptPath)
    topDir = os.path.join(scriptDir, '..', '..', '..')
    topDir = os.path.abspath(topDir)
    sys.path.append(topDir)
    
    topDir = os.path.join(scriptDir, '..', '..')
    topDir = os.path.abspath(topDir)
    sys.path.append(topDir)
    
    os.environ['DJANGO_SETTINGS_MODULE'] ='cjp.settings'
    
setPathToDjango(__file__)

# https://djangosnippets.org/snippets/1170/
def batch_qs(qs, batch_size=100):
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield (start, end, total, qs[start:end])

from django import db
from cjp.newsarticles.models import Article
from cjp.textanalysis.models import ArticleWord, Word
from time import sleep
from datetime import datetime
now = datetime.now

article_qs = Article.objects.order_by('id')
cnt = 0
for start, end, total, qs in batch_qs(article_qs):
    for article in qs:
        ArticleWord.processArticle(article)
        cnt += 1
        sleep(.25)
        
        if cnt % 10 == 0:
            print now(), ": processed", cnt, "articles"
    
    # prevents memory leaks in debug mode
    db.reset_queries()
    
for table in (Word, ArticleWord):
    table.objects.raw('VACUUM ANALYZE %s' % table._meta.db_table)