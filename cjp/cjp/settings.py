# Django settings for cjp project.
import os.path
from os import environ

#
# 2/18/2012 JN
# Set the environment variable CJP_DJANGO_DEVELOPMENT to enable development mode.
# Must also be set when testing scrapers in the scripts directory
# Can make multiple configs if necessary
# Raises an error if the enviromental variable exists but is not known
#
# If environment variable is missing, assumes production
#
if "CJP_DJANGO_DEVELOPMENT" in environ:
    #######################
    #  DEVELOPMENT SETTINGS
    #######################
    if environ["CJP_DJANGO_DEVELOPMENT"] == "TestConfig_1":
        print "---Running Development Config---"
        CJP_ROOT = "/cjpdata"
        CJP_ADMIN_USER = "cjpadmin"

        DEBUG = True

        ADMINS = (
            # ('Your Name', 'your_email@example.com'),
        )

        DATABASES = {
            'default': {
                #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'ENGINE': 'django.contrib.gis.db.backends.postgis',
                'NAME': 'cjpwebdb',                      # Or path to database file if using sqlite3.
                'USER': 'cjpuser',                      # Not used with sqlite3.
                'PASSWORD': 'cjppasswd',                  # Not used with sqlite3.
                'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
            }
        }
    else:
        raise ValueError("Bad value for environment variable CJP_DJANGO_DEVELOPMENT: %s" % environ["CJP_DJANGO_DEVELOPMENT"])
else:
    #######################
    # PRODUCTION SETTINGS
    #######################

    # 2011-12-20 use vhost with root at /
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

    DATABASES = {
        'default': {
            #'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'cjpwebdb',                      # Or path to database file if using sqlite3.
            'USER': 'cjpuser',                      # Not used with sqlite3.
            'PASSWORD': 'cjppasswd',                  # Not used with sqlite3.
            'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

MANAGERS = ADMINS

TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/var/cjpstatic'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/cjpstatic/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'staticfiles'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '#&ubnzmo6$-0nk7i&hmii=e$7y-)nv+bm#&ps)6eq@!k+n-nq5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.transaction.TransactionMiddleware',
)

ATOMIC_REQUESTS = True
# RE: deprecation of TransactionMiddleware & introduction of ATOMIC_REQUESTS
# see: https://docs.djangoproject.com/en/1.6/topics/db/transactions/#changes-from-django-1-5-and-earlier

#ROOT_URLCONF = 'cjp.urls'
ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates'),
)

INSTALLED_APPS = (
    'newsarticles',
    'crimedata',
    'textanalysis',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    'django.contrib.gis',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 2/18/2012 JN
# added timeout for cookies
SESSION_COOKIE_AGE = 60 * 60 * 24

LOGIN_REDIRECT_URL = CJP_ROOT;

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


