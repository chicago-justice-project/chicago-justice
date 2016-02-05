import os
import site
import sys

site.addsitedir('/home/cjp/env/chicagojustice/lib/python2.7/site-packages')
sys.path.append('/home/cjp/sites/chicago-justice/cjp')
sys.stdout = sys.stderr

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cjp.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
