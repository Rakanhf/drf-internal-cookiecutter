# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

import os
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent.parent


SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)


ALLOWED_HOSTS = config("ALLOWED_HOSTS", default=[], cast=Csv())


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "phonenumber_field",
    "django_filters",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_email",
    "two_factor",
    "two_factor.plugins.phonenumber",
    "django_user_agents",
    "django_rest_passwordreset",
    "drf_standardized_errors",
    "auditlog",
    "corsheaders",
    "core",
    "authentication",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.JWTAuthenticationMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]

ROOT_URLCONF = "mainbrain.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mainbrain.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "authentication.backends.JWTAuthentication",
        "authentication.backends.TemporaryTokenAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "authentication.throttling.LoginThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "9999/minute",
        "login": "9999/minute",
    },
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
}


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "sslmode": "require",
    }
}

AUTH_USER_MODEL = "core.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_LIFETIME_HOURS": 3,
    "TOKEN_OBTAIN_SERIALIZER": "authentication.serializers.CustomTokenObtainPairSerializer",
}


OTP_DEVICE_CLASSES = {
    "sms": "phonenumber.PhoneDevice",
    "totp": "otp_totp.TOTPDevice",
    "email": "authentication.CustomEmailDevice",
}

DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 1  # in hours
DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE = True

DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    "CLASS": "django_rest_passwordreset.tokens.RandomStringTokenGenerator",
    "OPTIONS": {"min_length": 20, "max_length": 30},
}

RESET_PASSWORD_URL = "http://localhost:3000/auth/reset-password/"

# ------------------------ OTP --------------------------
OTP_EMAIL_TOKEN_VALIDITY = 60 * 10  # 5 minutes
TOKEN_EXPIRATION_TIME = timedelta(minutes=5)
OTP_EMAIL_BODY_TEMPLATE = os.path.join(
    BASE_DIR, "core/templates/emails/auth/email_otp.html"
)
OTP_SMS_BODY_TEMPLATE = os.path.join(
    BASE_DIR, "core/templates/emails/auth/sms_otp.html"
)
OTP_EMAIL_SUBJECT = "OTP for login"
TWO_FACTOR_SMS_GATEWAY = "authentication.gateways.CustomTwilioGateWay"
TWILIO_CALLER_ID = config("TWILIO_PHONE_NUMBER")
# ------------------------ OTP --------------------------


# ------------------------ Email ------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")
# ------------------------ Email ------------------------


# ------------------------ SMS --------------------------------
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER")
# ------------------------ SMS --------------------------------

STATICFILES_DIRS = [os.path.join(BASE_DIR, "core/static")]


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
