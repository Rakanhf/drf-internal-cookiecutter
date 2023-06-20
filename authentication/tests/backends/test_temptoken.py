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
from rest_framework.exceptions import AuthenticationFailed
from core.models import ExpiringToken
from authentication.backends import TemporaryTokenAuthentication
from datetime import timedelta
from unittest import mock

User = get_user_model()


class TemporaryTokenAuthenticationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="testuser@test.com", password="password"
        )
        self.token = ExpiringToken.objects.create(user=self.user)
        self.auth = TemporaryTokenAuthentication()

    def test_authenticate_valid_token(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer " + self.token.key)

        user, token = self.auth.authenticate(request)

        self.assertEqual(user, self.user)
        self.assertEqual(token, self.token)

    def test_authenticate_no_authorization_header(self):
        request = self.factory.get("/")

        result = self.auth.authenticate(request)

        self.assertIsNone(result)

    def test_authenticate_no_token(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer ")

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_invalid_token_format(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer token1 token2")

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_invalid_token(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer invalidtoken")

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_expired_token(self):
        # Save the token with a future expiration date.
        self.token.save()
        # Prepare a request with the token
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer " + self.token.key)
        # Move forward in time beyond the token's expiration
        with mock.patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = self.token.expires_at + timedelta(minutes=10)
            # Now the token should be expired, so authenticate should raise an exception
            with self.assertRaises(AuthenticationFailed):
                self.auth.authenticate(request)

    def test_authenticate_unicode_error(self):
        # use a non-ascii character in the token
        bad_token = "Bearer " + "token_with_ñ"
        request = self.factory.get("/fake-endpoint")
        request.META["HTTP_AUTHORIZATION"] = bad_token
        with self.assertRaises(AuthenticationFailed) as context_manager:
            self.auth.authenticate(request)
        self.assertEqual(
            str(context_manager.exception),
            "Invalid token header. Token string should not contain invalid characters.",
        )
