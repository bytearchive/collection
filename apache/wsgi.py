from django.core.handlers.wsgi import WSGIHandler

import pinax.env

# django-celery needs this two lines
import os
os.environ["CELERY_LOADER"] = "django"

# setup the environment for Django and Pinax
pinax.env.setup_environ(__file__)


# set application for WSGI processing
application = WSGIHandler()
