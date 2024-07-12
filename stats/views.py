import datetime
from django.contrib.auth.models import User
from crimedata.models import CrimeReport
from newsarticles.models import Article, Category, NewsSource, UserCoding
from django.db import connection
from django.db.models import Count
from django.shortcuts import render
from django.template import RequestContext

def totalCounts(request):
    cursor = connection.cursor()

    totals = []

    totals.append(('CrimeReport', CrimeReport.objects.count()))

    for source in NewsSource.objects.all():
        source_count = Article.objects.filter(news_source=source, relevant=True).count()

        totals.append((source.name, source_count))

    data = {
        'totals': totals,
        'articleNonRelevantCount': Article.objects.filter(relevant=False).count()
    }

    cursor.execute("""SELECT COUNT(DISTINCT article_id) AS count
        FROM newsarticles_article a, newsarticles_article_categories nac
        WHERE a.relevant=TRUE AND a.id=nac.article_id""")
    data['categorizedArticleCount'] = cursor.fetchone()[0]

    return render(request, 'stats/totalCounts.html', data)

def userCounts(request):
    totals = []

    for user in User.objects.all():
        user_count = UserCoding.objects.filter(user=user).count()
        totals.append((user.username, user_count))

    data = {
        'totals': totals,
    }

    return render(request, 'stats/userCounts.html', data)

