# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from core.models import UserDevice


class TestUserDeviceEndpoint(APITestCase):
    def setUp(self):
        # This method will run before any test.

        self.client = APIClient()
        self.client2 = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpassword",
            phone_number="+905000000000",
            is_superuser=True,
        )
        self.user2 = get_user_model().objects.create_user(
            email="testuser2@test.com",
            password="testpassword",
            phone_number="+905000000002",
            is_superuser=True,
        )
        self.group = Group.objects.create(name="testgroup")
        self.group2 = Group.objects.create(name="testgroup2")
        self.device = UserDevice.objects.create(user=self.user, ip_address="127.0.0.1")
        self.device2 = UserDevice.objects.create(
            user=self.user2, ip_address="127.0.0.2"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_user_device_list(self):
        """
        Ensure we can get list of user users_devices.
        """
        response = self.client.get(reverse("accounts:users_devices-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_device_detail(self):
        """
        Ensure we can get a user device detail.
        """
        response = self.client.get(
            reverse("accounts:users_devices-detail", args=[self.device.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_device(self):
        """
        Ensure we can't create a new user device.
        """
        data = {
            "ip_address": "127.0.0.1",
            "user": self.user.id,
            "user_agent": "desktop",
        }
        response = self.client.post(reverse("accounts:users_devices-list"), data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_device(self):
        """
        Ensure we can update a user device.
        """
        data = {
            "ip_address": "127.0.0.12",
            "user": self.user.id,
            "user_agent": "desktop",
        }
        response = self.client.put(
            reverse("accounts:users_devices-detail", args=[self.device.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_device(self):
        """
        Ensure we can delete a user device.
        """
        response = self.client.delete(
            reverse("accounts:users_devices-detail", args=[self.device.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_partial_update_with_another_user(self):
        """
        Ensure we can't partial update a user device with another user.
        """
        data = {
            "ip_address": "127.0.0.15",
        }
        response = self.client.patch(
            reverse("accounts:users_devices-detail", args=[self.device2.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
