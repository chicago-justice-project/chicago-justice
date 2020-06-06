from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from rest_framework import routers

import django.contrib.auth.views
import cjpusers.views
import stats.views
import crimedata.views
import newsarticles.views

from newsarticles.api_views import router_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/', include(router_urls())),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # user login and admin
    url(r'^user/login/$', django.contrib.auth.views.login, name='login'),
    url(r'^user/logout/$', django.contrib.auth.views.logout, kwargs={'next_page': 'mainArticleView'}, name='logout'),
    url(r'^user/manage/$', cjpusers.views.manage, name='userManageView'),
    url(r'^user/manage/adduser/$', cjpusers.views.manage, kwargs={'action': 'addUser'}, name='userManageAddUserView'),
    url(r'^user/manage/update/(\d+)/$', cjpusers.views.userUpdate, name='userUpdate'),

    # toplevel article
    url(r'^$', newsarticles.views.articleList),
    url(r'^articles/$', newsarticles.views.articleList, name='mainArticleView'),

    #individual article
    url(r'^articles/(\d+)/$', newsarticles.views.view_article, name='view-article'),
    url(r'^articles/(\d+)/updatecoding/$', newsarticles.views.code_article, name='code-article'),
    url(r'^articles/coderandom/$', newsarticles.views.random_article, name='random-article'),
    url(r'^articles/help/$', newsarticles.views.help, name='help'),

    # crime reports
    url(r'^crimereports/$', crimedata.views.crimeReportList, name='mainCrimeReportView'),
    url(r'^crimereports/export/$', crimedata.views.crimeReportExport, name='exportCrimeReport'),

    # individual crime reports
    url(r'^crimereports/(\d+)/$', crimedata.views.crimeReportView, name='viewSingleCrimeReport'),

    # stats
    url(r'^stats/totalCounts$', stats.views.totalCounts, name='statsTotalCounts'),
    url(r'^stats/categorySearch$', newsarticles.views.categoryXTab, name='categoryXTab')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^debug/', include(debug_toolbar.urls)),
    ]

urlpatterns += staticfiles_urlpatterns()
