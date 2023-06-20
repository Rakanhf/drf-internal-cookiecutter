#!/usr/bin/env python
# Project: MainBrain
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)  
#           @Netoceans                 
#           Rakan Farhouda
#


"""Django's command-line utility for administrative tasks."""
import os
import sys
from mainbrain.settings import base


def main():
    """Run administrative tasks."""
    if base.DEBUG:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainbrain.settings.dev')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainbrain.settings.prod')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
