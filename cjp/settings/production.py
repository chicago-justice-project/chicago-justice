#######################
# PRODUCTION SETTINGS
#######################

from .base import *

ALLOWED_HOSTS = [
    'data.chicagojustice.org',
    '.amazonaws.com',
    '.elasticbeanstalk.com',
]

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
STATIC_ROOT = os.path.join(BASE_DIR, "public-static")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cjpweb_prd',
        'USER': 'cjpuser',
        'PASSWORD': 'cjpuser',
        'HOST': 'chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com',
        'PORT': '',
    }
}

EMAIL_HOST = get_env_variable('EMAIL_HOST')
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
