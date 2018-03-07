from .base import *

print("---Running Local Config---")

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
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': get_env_variable('DATABASE_NAME'),                      # Or path to database file if using sqlite3.
        'USER': get_env_variable('DATABASE_USER'),                      # Not used with sqlite3.
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
