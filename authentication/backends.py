# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed, ParseError
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object

from core.models import ExpiringToken

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        jwt_token = request.META.get("HTTP_AUTHORIZATION")
        if jwt_token is None:
            return None

        jwt_token = JWTAuthentication.get_the_token_from_header(
            jwt_token
        )  # clean the token

        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(
                jwt_token,
                settings.SECRET_KEY,
                algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
            )
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed("Invalid signature")
        except Exception:
            raise ParseError()

        # Get the user from the database
        email_or_phone_number = payload.get("user_identifier")
        if email_or_phone_number is None:
            raise AuthenticationFailed("User identifier not found in JWT")

        user = User.objects.filter(email=email_or_phone_number).first()
        if user is None:
            user = User.objects.filter(phone_number=email_or_phone_number).first()
            if user is None:
                raise AuthenticationFailed("User not found")

        # Return the user and token payload
        return user, payload

    def authenticate_header(self, request):
        return "Bearer"

    @classmethod
    def create_jwt(cls, user):
        # Create the JWT payload
        payload = {
            "user_identifier": user.email,
            "exp": int(
                (
                    datetime.now()
                    + timedelta(hours=settings.SIMPLE_JWT["TOKEN_LIFETIME_HOURS"])
                ).timestamp()
            ),
            # set the expiration time for 5 hour from now
            "iat": datetime.now().timestamp(),
            "email": user.email,
            "phone_number": user.phone_number,
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT["ALGORITHM"]
        )

        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace("Bearer", "").replace(" ", "")  # clean the token
        return token


class TemporaryTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b"bearer":
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)
        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _(
                "Invalid token header. Token string should not contain invalid characters."
            )
            raise exceptions.AuthenticationFailed(msg)
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        token = self.get_token(key)
        self.check_expiration(token)
        return (token.user, token)

    def get_token(self, key):
        try:
            return ExpiringToken.objects.select_related("user").get(key=key)
        except ExpiringToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

    def check_expiration(self, token):
        if token.is_expired:
            raise exceptions.AuthenticationFailed(_("Token has expired."))


class TemporaryTokenAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = TemporaryTokenAuthentication  # replace with your import path
    name = 'TemporaryTokenAuth'

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(header_name='Authorization', token_prefix='Bearer')