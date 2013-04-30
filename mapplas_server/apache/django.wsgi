import os, sys

sys.path.append('/home/ubuntu/ENV/server/mapplas_server/')
sys.path.append('/home/ubuntu/ENV/server/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mapplas_server.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()