import os
import sys

scriptPath = os.path.realpath(__file__)
scriptDir = os.path.dirname(scriptPath)

path = scriptDir
if path not in sys.path:
    sys.path.append(path)

path = os.path.join(scriptDir, 'cjp')
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'cjp.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

