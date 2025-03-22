from django.conf import settings
from django.urls import include, path, re_path
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
    path('admin/', admin.site.urls),

    path('api/', include(router_urls())),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # user login and admin
    path('user/login/', django.contrib.auth.views.LoginView.as_view(), name='login'),
    path('user/logout/', django.contrib.auth.views.LogoutView.as_view(next_page='mainArticleView'), name='logout'),
    path('user/manage/', cjpusers.views.manage, name='userManageView'),
    path('user/manage/adduser/', cjpusers.views.manage, kwargs={'action': 'addUser'}, name='userManageAddUserView'),
    re_path(r'^user/manage/update/(\d+)/$', cjpusers.views.userUpdate, name='userUpdate'),

    # toplevel article
    path('', newsarticles.views.articleList),
    path('articles/', newsarticles.views.articleList, name='mainArticleView'),

    #individual article
    re_path(r'^articles/(\d+)/$', newsarticles.views.view_article, name='view-article'),
    re_path(r'^articles/(\d+)/updatecoding/$', newsarticles.views.code_article, name='code-article'),
    path('articles/coderandom/', newsarticles.views.random_article, name='random-article'),
    path('articles/help/', newsarticles.views.help, name='help'),

    # crime reports
    path('crimereports/', crimedata.views.crimeReportList, name='mainCrimeReportView'),
    path('crimereports/export/', crimedata.views.crimeReportExport, name='exportCrimeReport'),

    # individual crime reports
    re_path(r'^crimereports/(\d+)/$', crimedata.views.crimeReportView, name='viewSingleCrimeReport'),

    # stats
    path(r'^stats/totalCounts$', stats.views.totalCounts, name='statsTotalCounts'),
    path(r'^stats/categorySearch$', newsarticles.views.categoryXTab, name='categoryXTab'),
    path(r'^stats/userCounts$', stats.views.userCounts, name='statsUserCounts')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('debug/', include(debug_toolbar.urls)),
    ]

urlpatterns += staticfiles_urlpatterns()
