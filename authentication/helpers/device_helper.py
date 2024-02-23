# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from django.apps import apps
from django.conf import settings

def get_device_classes():
    """
    Retrieves configured device classes for OTP (One-Time Passwords).

    Handles the potential absence of the 'OTP_DEVICE_CLASSES' setting in 
    Django settings, providing an empty dictionary as a default. Also 
    catches and suppresses errors from 'apps.get_model', treating any 
    problematic entries as None.

    Returns:
        dict: A dictionary mapping device class names to their corresponding models.
    """

    try:
        return {
            key: apps.get_model(val)
            for key, val in settings.OTP_DEVICE_CLASSES.items()
        }
    except AttributeError:
        return {}  # Default if OTP_DEVICE_CLASSES is missing
    except LookupError as error:
        return {}
