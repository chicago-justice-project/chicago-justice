from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'cjp.views.home', name='home'),
    # url(r'^cjp/', include('cjp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # user login and admin
    url(r'^user/login/$', 'django.contrib.auth.views.login', name='loginView'),
    url(r'^user/logout/$', 'django.contrib.auth.views.logout', kwargs={'next_page': 'mainArticleView'}, name='logoutView'),
    url(r'^user/manage/$', 'cjpusers.views.manage', name='userManageView'),
    url(r'^user/manage/adduser/$', 'cjpusers.views.manage', kwargs={'action': 'addUser'}, name='userManageAddUserView'),
    url(r'^user/manage/update/(\d+)/$', 'cjpusers.views.userUpdate', name='userUpdate'),

    # toplevel article
    url(r'^$', 'newsarticles.views.articleList'),
    url(r'^articles/$', 'newsarticles.views.articleList', name='mainArticleView'),

    #individual article
    url(r'^articles/(\d+)/$', 'newsarticles.views.view_article', name='view-article'),
    url(r'^articles/(\d+)/updatecoding/$', 'newsarticles.views.code_article', name='code-article'),

    # crime reports
    url(r'^crimereports/$', 'crimedata.views.crimeReportList', name='mainCrimeReportView'),
    url(r'^crimereports/export/$', 'crimedata.views.crimeReportExport', name='exportCrimeReport'),

    # individual crime reports
    url(r'^crimereports/(\d+)/$', 'crimedata.views.crimeReportView', name='viewSingleCrimeReport'),

    # stats
    url(r'^stats/totalCounts$', 'stats.views.totalCounts', name='statsTotalCounts'),

]

urlpatterns += staticfiles_urlpatterns()

