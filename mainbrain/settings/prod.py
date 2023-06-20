# Project: WeCare
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Netoceans
#           Rakan Farhouda
#


from mainbrain.settings.base import *

# ------------------------ LOGGING ------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
# ------------------------ LOGGING ------------------------


# ------------------------ STATIC ------------------------
# STATIC_ROOT = "/var/www/example.com/static/"
# MEDIA_ROOT = "/var/www/example.com/static/"
# ------------------------ STATIC ------------------------

# ------------------------ CORS --------------------------
# CORE_ORIGIN_WHITELIST = ["http://127.0.0.1:3000", "http://localhost:3000"]
# CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:3000", "http://localhost:3000"]
# CORS_ALLOW_CREDENTIALS = True
# ------------------------ CORS --------------------------
