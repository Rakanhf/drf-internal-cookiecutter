# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from authentication.backends import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ParseError
from datetime import datetime, timedelta
import jwt
from django.conf import settings


User = get_user_model()


class JWTAuthenticationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.auth = JWTAuthentication()

    def test_authenticate_valid_token(self):
        jwt_token = self.auth.create_jwt(self.user)
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer " + jwt_token)

        user, payload = self.auth.authenticate(request)

        self.assertEqual(user, self.user)
        self.assertEqual(payload["user_identifier"], self.user.email)

    def test_authenticate_invalid_token(self):
        import jwt

        invalid_token_payload = {"some": "payload"}
        invalid_token = jwt.encode(
            invalid_token_payload, "wrong-secret", algorithm="HS256"
        )

        request = RequestFactory().get("/fake-endpoint")
        request.META = {
            "HTTP_AUTHORIZATION": "Bearer " + invalid_token,
        }
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_no_token(self):
        request = self.factory.get("/")

        result = self.auth.authenticate(request)

        self.assertIsNone(result)

    def test_authenticate_malformed_token(self):
        invalid_token = "this-is-not-a-token"
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer " + invalid_token)
        with self.assertRaises(ParseError):
            self.auth.authenticate(request)

    def test_authenticate_token_without_user_identifier(self):
        payload = {
            "exp": int(
                (
                    datetime.now()
                    + timedelta(
                        hours=settings.SIMPLE_JWT[
                            "ACCESS_TOKEN_LIFETIME"
                        ].total_seconds()
                        // 3600
                    )
                ).timestamp()
            )
        }
        invalid_token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT["ALGORITHM"]
        )
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer " + invalid_token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_token_with_non_existing_user(self):
        payload = {
            "user_identifier": "non-existing@test.com",
            "exp": int(
                (
                    datetime.now()
                    + timedelta(
                        hours=settings.SIMPLE_JWT[
                            "ACCESS_TOKEN_LIFETIME"
                        ].total_seconds()
                        // 3600
                    )
                ).timestamp()
            ),
        }
        invalid_token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT["ALGORITHM"]
        )
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer " + invalid_token)
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_header(self):
        request = self.factory.get("/")
        result = self.auth.authenticate_header(request)
        self.assertEqual(result, "Bearer")
