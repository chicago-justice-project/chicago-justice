from crimedata.models import CrimeReport
from newsarticles.models import Article, FEED_NAMES, Category
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

def totalCounts(request):
    categories = Category.objects.all()
    
    data = {}
    data['totals'] = [ ('CrimeReport', CrimeReport.objects.count()), ] + [
                            (fullname, Article.objects.filter(feedname=feedId, relevant=True).count())
                                for (feedId, fullname) in FEED_NAMES
                     ]
    
    data['articleNonRelevantCount'] = Article.objects.filter(relevant=False).count()
    data['categorizedArticleCount'] = Article.objects.filter(relevant=True, categories__in = categories).distinct().count()
    
    return render_to_response('stats/totalCounts.html', data,
                          context_instance=RequestContext(request))
    
def yearlyCounts(request):
    data = {}
    
    data['years'] = [
            ('CrimeReport', CrimeReport.objects.extra(
                                            select={'the_year': 'EXTRACT(year FROM crime_date)'}
                                        ).values('the_year').annotate(year_count=Count('id')).order_by('the_year')), ] + [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                            select={'the_year': 'EXTRACT(year FROM created)'}
                                        ).values('the_year').annotate(year_count=Count('id')).order_by('the_year'))
                for (feedId, fullname) in FEED_NAMES
        ]
     
    return render_to_response('stats/yearlyCounts.html', data,
                          context_instance=RequestContext(request))
    
def monthlyCounts(request):
    data = {}
    
    data['monthCrimeReport'] = CrimeReport.objects.extra(
                                            select={'the_year': 'EXTRACT(year FROM crime_date)',
                                                    'the_month': "to_char(crime_date, 'YYYY-MM')"}
                                        ).values('the_month', 'the_year').annotate(month_count=Count('id')).order_by('the_year', 'the_month')
                                        
            
    data['monthFeeds'] = [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                            select={'the_year': 'EXTRACT(year FROM created)',
                                                    'the_month': "to_char(created, 'YYYY-MM')"}
                                        ).values('the_month', 'the_year').annotate(month_count=Count('id')).order_by('the_year', 'the_month'))
                for (feedId, fullname) in FEED_NAMES
        ]
     
    return render_to_response('stats/monthlyCounts.html', data,
                          context_instance=RequestContext(request))
    
def dailyCounts(request):
    data = {}
    
    data['dayCrimeReport'] = CrimeReport.objects.extra(
                                            select={'the_date': "to_char(crime_date, 'YYYY-MM-DD')"}
                                        ).values('crime_date', 'the_date').annotate(day_count=Count('id')).order_by('crime_date')
            
            
    data['dayFeeds'] = [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                           select={'the_year' :  'EXTRACT(year FROM created)',
                                                    'the_month': 'EXTRACT(month FROM created)',
                                                    'the_day' :  'EXTRACT(day FROM created)',
                                                    'the_date' : "to_char(created, 'YYYY-MM-DD')"}
                                        ).values('the_date', 'the_day', 'the_month', 'the_year').annotate(day_count=Count('id')).order_by('the_year', 'the_month', 'the_day'))
                for (feedId, fullname) in FEED_NAMES
        ]
            
    data['days'] = [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                            select={'the_year' : 'EXTRACT(year FROM created)',
                                                    'the_month': 'EXTRACT(month FROM created)',
                                                    'the_date' : 'EXTRACT(day FROM created)'}
                                        ).values('the_date','the_month', 'the_year').annotate(day_count=Count('id')).order_by('the_year', 'the_month', 'the_date'))
                for (feedId, fullname) in FEED_NAMES
        ]
     
    return render_to_response('stats/dailyCounts.html', data,
                          context_instance=RequestContext(request))  

def viewStats(request):
    
    categories = Category.objects.all()
    
    data = {
            
        'totals' : [ ('CrimeReport', CrimeReport.objects.count()), ] + [
                (fullname, Article.objects.filter(feedname=feedId, relevant=True).count())
                    for (feedId, fullname) in FEED_NAMES
            ],
            
        'years' : [
            ('CrimeReport', CrimeReport.objects.extra(
                                            select={'the_year': 'EXTRACT(year FROM crime_date)'}
                                        ).values('the_year').annotate(year_count=Count('id')).order_by('the_year')), ] + [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                            select={'the_year': 'EXTRACT(year FROM created)'}
                                        ).values('the_year').annotate(year_count=Count('id')).order_by('the_year'))
                for (feedId, fullname) in FEED_NAMES
        ],
            
        'monthCrimeReport' : CrimeReport.objects.extra(
                                            select={'the_year': 'EXTRACT(year FROM crime_date)',
                                                    'the_month': "to_char(crime_date, 'YYYY-MM')"}
                                        ).values('the_month', 'the_year').annotate(month_count=Count('id')).order_by('the_year', 'the_month'),
                                        
            
        'monthFeeds' : [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                            select={'the_year': 'EXTRACT(year FROM created)',
                                                    'the_month': "to_char(created, 'YYYY-MM')"}
                                        ).values('the_month', 'the_year').annotate(month_count=Count('id')).order_by('the_year', 'the_month'))
                for (feedId, fullname) in FEED_NAMES
        ],
            
        'dayCrimeReport' : CrimeReport.objects.extra(
                                            select={'the_date': "to_char(crime_date, 'YYYY-MM-DD')"}
                                        ).values('crime_date', 'the_date').annotate(day_count=Count('id')).order_by('crime_date'),
            
            
        'dayFeeds' : [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                           select={'the_year' :  'EXTRACT(year FROM created)',
                                                    'the_month': 'EXTRACT(month FROM created)',
                                                    'the_day' :  'EXTRACT(day FROM created)',
                                                    'the_date' : "to_char(created, 'YYYY-MM-DD')"}
                                        ).values('the_date', 'the_day', 'the_month', 'the_year').annotate(day_count=Count('id')).order_by('the_year', 'the_month', 'the_day'))
                for (feedId, fullname) in FEED_NAMES
        ],
            
        'days' : [
            (fullname, Article.objects.filter(feedname=feedId, relevant=True).extra(
                                            select={'the_year' : 'EXTRACT(year FROM created)',
                                                    'the_month': 'EXTRACT(month FROM created)',
                                                    'the_date' : 'EXTRACT(day FROM created)'}
                                        ).values('the_date','the_month', 'the_year').annotate(day_count=Count('id')).order_by('the_year', 'the_month', 'the_date'))
                for (feedId, fullname) in FEED_NAMES
        ],
        
        'articleNonRelevantCount' : Article.objects.filter(relevant=False).count(),
        'categorizedArticleCount' : Article.objects.filter(relevant=True, categories__in = categories).distinct().count(),
        
    }
    
    # Don't `print` when using WSGI; use Python/Django logging.* instead.
    #print connection.queries
    
    return render_to_response('stats/stats.html', data,
                          context_instance=RequestContext(request))
