# Project: MainBrain
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)  
#           @Netoceans                 
#           Rakan Farhouda
#


"""
ASGI config for mainbrain project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from mainbrain.settings import base

if base.DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainbrain.settings.dev')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainbrain.settings.prod')

application = get_asgi_application()
