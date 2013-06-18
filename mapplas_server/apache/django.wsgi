import os, sys
import djcelery

djcelery.setup_loader()

sys.path.append('/home/ubuntu/server/mapplas_server/')
sys.path.append('/home/ubuntu/server/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'mapplas_server.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()