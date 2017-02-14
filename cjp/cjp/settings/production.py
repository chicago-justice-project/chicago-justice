#######################
# PRODUCTION SETTINGS
#######################

from .base import *

ALLOWED_HOSTS = [
    'ec2-54-88-218-235.compute-1.amazonaws.com',
    'data.chicagojustice.org',
]
POSTGIS_VERSION = (2, 1, 8)

CJP_ROOT = "/"
CJP_ADMIN_USER = "cjpadmin"

DEBUG = False

ADMINS = (
    ('Chris Shenton', 'chris@koansys.com',),
    # 2012-01-22 chris@koansys.com: missing 404.html sends tons of mail, don't bother Tracy
    #('Tracy Siska',   'tsiska@chicagojustice.org',),
    ("Reed O'Brien", 'reed@koansys.com',),
    # ('Your Name', 'your_email@example.com'),
)

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/usr/share/nginx/chicagojustice'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
# TODO: fix nginx config to serve out of separate static dir
STATIC_URL = '/'

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cjpweb_prd',
        'USER': 'cjpuser',
        'PASSWORD': 'cjpuser',
        'HOST': 'chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com',
        'PORT': '',
    }
}
