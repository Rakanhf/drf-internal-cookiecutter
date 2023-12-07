# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


"""
WSGI config for mainbrain project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from mainbrain.settings import base

if base.DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainbrain.settings.dev")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainbrain.settings.prod")

application = get_wsgi_application()
