import datetime
from crimedata.models import CrimeReport
from newsarticles.models import Article, Category, NewsSource
from django.db import connection
from django.db.models import Count
from django.shortcuts import render_to_response
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

    return render_to_response('stats/totalCounts.html', data,
                              context_instance=RequestContext(request))

def yearlyCounts(request):
    data = {}

    all_counts = []

    crime_count = CrimeReport.objects.extra(
        select={'the_year': 'EXTRACT(year FROM crime_date)'}
    ).values('the_year') \
        .annotate(year_count=Count('id')) \
        .order_by('the_year')

    all_counts.append(('CrimeReport', crime_count))

    for source in NewsSource.objects.all():
        source_count = Article.objects.filter(news_source=source, relevant=True) \
                .extra(select={'the_year': 'EXTRACT(year FROM created)'}) \
                .values('the_year').annotate(year_count=Count('id')).order_by('the_year')
        all_counts.append((source.name, source_count))

    data['years'] = all_counts

    return render_to_response('stats/yearlyCounts.html', data,
                              context_instance=RequestContext(request))

def monthlyCounts(request):
    data = {}

    data['monthCrimeReport'] = CrimeReport.objects.extra(select={
        'the_year': 'EXTRACT(year FROM crime_date)',
        'the_month': "to_char(crime_date, 'YYYY-MM')"
    }).values('the_month', 'the_year') \
        .annotate(month_count=Count('id')) \
        .order_by('the_year', 'the_month')

    month_feeds = []

    for source in NewsSource.objects.all():
        counts = Article.objects.filter(news_source=source, relevant=True) \
                    .extra(select={
                        'the_year': 'EXTRACT(year FROM created)',
                        'the_month': "to_char(created, 'YYYY-MM')"
                    }) \
                    .values('the_month', 'the_year').annotate(month_count=Count('id')) \
                    .order_by('the_year', 'the_month')

        month_feeds.append((source.name, counts))

    data = {
        'monthFeeds': month_feeds,
        'monthCrimeReport': month_crime_report
    }

    return render_to_response('stats/monthlyCounts.html', data,
                              context_instance=RequestContext(request))

def dailyCounts(request):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=60)
    date_range = (start_date, end_date)

    data = {}

    day_crime_report = CrimeReport.objects \
        .extra(select={'the_date': "to_char(crime_date, 'YYYY-MM-DD')"}) \
        .values('crime_date', 'the_date').annotate(day_count=Count('id')) \
        .order_by('crime_date')

    day_feeds = []
    for source in NewsSource.objects.all():
        counts = Article.objects.filter(news_source=source, relevant=True, created__range=date_range) \
            .extra(select={
                'the_year': 'EXTRACT(year FROM created)',
                'the_month': 'EXTRACT(month FROM created)',
                'the_day':  'EXTRACT(day FROM created)',
                'the_date': "to_char(created, 'YYYY-MM-DD')"
            }).values('the_date', 'the_day', 'the_month', 'the_year') \
                .annotate(day_count=Count('id')).order_by('the_year', 'the_month', 'the_day')

        day_feeds.append((source.name, counts))

    days = []
    for source in NewsSource.objects.all():
        counts = Article.objects.filter(news_source=source, relevant=True, created__range=date_range) \
            .extra(select={
                'the_year': 'EXTRACT(year FROM created)',
                'the_month': 'EXTRACT(month FROM created)',
                'the_date': 'EXTRACT(day FROM created)'
            }).values('the_date', 'the_month', 'the_year') \
                .annotate(day_count=Count('id')) \
                .order_by('the_year', 'the_month', 'the_date')

        days.append((source.name, counts))

    data = {
        'dayCrimeReport': day_crime_report,
        'dayFeeds': day_feeds,
        'days': days,
    }

    return render_to_response('stats/dailyCounts.html', data,
                              context_instance=RequestContext(request))

