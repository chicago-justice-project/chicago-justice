from .base import *

print("---Running Local Config---")
CJP_ADMIN_USER = "cjpadmin"

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Don't put anything in this directory yourself-
# just needs to be somewhere Django can write to
# TODO: fail hard if this doesn't exist
STATIC_ROOT = '/tmp/cjpstatic'

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
