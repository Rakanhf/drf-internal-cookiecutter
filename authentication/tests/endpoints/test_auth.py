# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from unittest.mock import patch
from rest_framework_simplejwt.exceptions import TokenError
from authentication.models import CustomEmailDevice
from core.models import UserDevice

User = get_user_model()


class CustomTokenObtainPairViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@test.com", password="testpass", phone_number="+905555555550"
        )
        self.user_otp = User.objects.create_user(
            email="testuser2@test.com",
            password="testpass",
            phone_number="+905555555551",
            enabled_2fa=True,
            default_2fa_method="email",
        )
        self.device = CustomEmailDevice.objects.create(
            user=self.user_otp, name="test device", confirmed=True
        )
        self.client = APIClient()

    def test_authenticate_successfully(self):
        data = {"email": "testuser@test.com", "password": "testpass"}
        response = self.client.post(reverse("authentication:token_obtain_pair"), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_authenticate_fail(self):
        data = {"email": "testuser@test.com", "password": "wrongpass"}
        response = self.client.post(reverse("authentication:token_obtain_pair"), data)
        self.assertEqual(response.status_code, 401)

    def test_authenticate_nonexistent_user(self):
        data = {"email": "nonexistent@test.com", "password": "testpass"}
        response = self.client.post(reverse("authentication:token_obtain_pair"), data)
        self.assertEqual(response.status_code, 401)

    @patch("authentication.helpers.otp_helper.OTPLoginFlowHelper.start_otp_flow")
    def test_start_otp_flow(self, start_otp_flow_mock):
        start_otp_flow_mock.return_value = None
        data = {
            "email": "testuser@test.com",
            "password": "testpass",
            "otp": "123456",  # OTP should be generated and known for this test
        }
        response = self.client.post(reverse("authentication:token_obtain_pair"), data)
        self.assertEqual(response.status_code, 200)

    @patch("authentication.views.OTPLoginFlowHelper.start_otp_flow")
    def test_token_error(self, start_otp_flow_mock):
        start_otp_flow_mock.side_effect = TokenError("Token is expired")
        data = {
            "email": "testuser@test.com",
            "password": "testpass",
        }
        response = self.client.post(reverse("authentication:token_obtain_pair"), data)
        self.assertEqual(response.status_code, 401)

    def test_response_from_start_otp_flow(self):
        data = {
            "email": "testuser2@test.com",
            "password": "testpass",
        }
        response = self.client.post(reverse("authentication:token_obtain_pair"), data)
        self.assertEqual(response.status_code, 202)


class TokenObtainPairViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", password="test1234", phone_number="+905555555550"
        )
        self.url = reverse("authentication:token_obtain_pair")

    def test_get_token_pair(self):
        response = self.client.post(
            self.url, {"email": "test@test.com", "password": "test1234"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)

    def test_invalid_credentials(self):
        response = self.client.post(
            self.url,
            {"email": "test@test.com", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_credentials(self):
        response = self.client.post(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_not_found(self):
        response = self.client.post(
            self.url, {"email": "user@user.com", "password": "test1234"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_not_active(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            self.url, {"email": "test@test.com", "password": "test1234"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.url, {"email": "test@test.com", "password": "test1234"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_existent_user(self):
        response = self.client.post(
            self.url,
            {"email": "notexist@test.com", "password": "test1234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_device_id_is_returned(self):
        response = self.client.post(
            self.url, {"email": "test@test.com", "password": "test1234"}, format="json"
        )
        user_device_id = (
            UserDevice.objects.filter(
                user=self.user,
            )
            .order_by("-last_login")
            .values_list("id", flat=True)
            .first()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_device_id"], int(user_device_id))


class OTPSetupViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@test.com", password="test1234")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.url = reverse("authentication:2fa_activate")

    def test_2fa_setup(self):
        response = self.client.post(self.url, {"type": "email"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("message" in response.data)

    def test_2fa_setup_invalid_type(self):
        response = self.client.post(self.url, {"type": "invalidtype"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_2fa_setup_no_type(self):
        response = self.client.post(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_2fa_setup_unauthenticated(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.post(
            self.url, {"type": "email"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OTPDisableViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", password="test1234", phone_number="+905555555550"
        )
        self.url = reverse("authentication:2fa_disable")

    def test_disable_otp_without_authentication(self):
        data = {
            "type": "all",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_disable_otp_with_authentication(self):
        data = {
            "type": "all",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_disable_otp_when_otp_already_disabled(self):
        data = {
            "type": "all",
        }
        # If OTP is already disabled for a user, the response might be different.
        self.client.force_authenticate(user=self.user)
        self.user.enabled_2fa = False
        self.user.save()
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "2FA has been disabled.")

    def test_disable_otp_without_types(self):
        data = {
            "type": "",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disable_otp_with_invalid_type(self):
        data = {
            "type": "invalidtype",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OTPVerifyViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", password="test1234", phone_number="+905555555550"
        )
        self.user_device = CustomEmailDevice.objects.create(
            user=self.user, name="test device", confirmed=False
        )
        self.user_device_confirmed = CustomEmailDevice.objects.create(
            user=self.user, name="test device", confirmed=True
        )
        self.url = reverse("authentication:2fa_verify")

    def test_verify_otp_without_authentication(self):
        data = {
            "otp_code": "123456",
            "user_device_id": self.user_device.id,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_otp_with_wrong_body(self):
        data = {
            "otp_code": "123456",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OTPResendViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", password="test1234", phone_number="+905555555550"
        )
        self.url = reverse("authentication:2fa_resend")

    def test_resend_otp_without_authentication(self):
        response = self.client.post(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_resend_otp_when_otp_is_not_enabled(self):
        self.client.force_authenticate(user=self.user)
        self.user.enabled_2fa = False
        self.user.save()
        response = self.client.post(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
