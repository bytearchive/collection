from django.core.handlers.wsgi import WSGIHandler

import pinax.env

# django-celery needs this two lines
import os
os.environ["CELERY_LOADER"] = "django"

# setup the environment for Django and Pinax
file_path = os.path.dirname(__file__)
project_path = os.path.dirname(file_path)
pinax.env.setup_environ(project_path=project_path)

# set application for WSGI processing
application = WSGIHandler()
