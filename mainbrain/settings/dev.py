# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from mainbrain.settings.base import *

# ------------------------ QUERY LOGING ------------------------
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#         },
#     },
# }
# ------------------------ QUERY LOGING ------------------------


CORE_ORIGIN_WHITELIST = ["http://127.0.0.1:3000", "http://localhost:3000"]
CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:3000", "http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = True
