import os
import site
import sys
from django.core.wsgi import get_wsgi_application

#site.addsitedir('/home/cjp/env/chicagojustice/lib/python2.7/site-packages')
#sys.path.append('/home/cjp/sites/chicago-justice/cjp')
sys.stdout = sys.stderr

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cjp.settings.local")

application = get_wsgi_application()
