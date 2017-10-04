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
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,      # Set to empty string for default. Not used with sqlite3.
    }
}
