"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("WSGI loaded")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

application = get_wsgi_application()
