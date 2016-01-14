# Django settings for cjp project in DEVELOPMENT mode.
# bin/django runserver --settings=cjp.settings_dev

import os.path
from settings import *


# Need debug on so that css etc are served from the MEDIA_ROOT
DEBUG = True

ADMINS = (
    ('Chris Shenton', 'chris@koansys.com',),
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = ''
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'staticfiles')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = '/var/cjpstatic'
STATIC_ROOT = '/tmp/cjpstatic'
#STATIC_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'staticfiles')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'staticfiles'),
)
