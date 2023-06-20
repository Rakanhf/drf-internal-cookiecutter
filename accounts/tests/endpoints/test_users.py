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


class TestUserEndpoint(APITestCase):
    def setUp(self):
        # This method will run before any test.

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpassword",
            phone_number="+905000000000",
            is_superuser=True,
        )
        self.group = Group.objects.create(name="testgroup")
        self.group2 = Group.objects.create(name="testgroup2")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_user_me(self):
        """
        Ensure we can get list of users.
        """
        response = self.client.get(reverse("accounts:users-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_list(self):
        """
        Ensure we can get list of users.
        """
        response = self.client.get(reverse("accounts:users-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_detail(self):
        """
        Ensure we can get a user detail.
        """
        response = self.client.get(
            reverse("accounts:users-detail", args=[self.user.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        """
        Ensure we can create a new user.
        """
        data = {
            "email": "testuser2@test.com",
            "phone_number": "+905123456715",
            "groups": [
                self.group.id,
            ],
        }
        response = self.client.post(reverse("accounts:users-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_user(self):
        """
        Ensure we can update a user.
        """
        data = {
            "email": "testuser2-update@test.com",
            "phone_number": "+905123456715",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "groups": [
                self.group.id,
                self.group2.id,
            ],
        }
        response = self.client.put(
            reverse("accounts:users-detail", args=[self.user.id]), data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_user(self):
        """
        Ensure we can partial update a user.
        """
        data = {
            "email": "testuser2-update@test-update.com",
        }
        response = self.client.patch(
            reverse("accounts:users-detail", args=[self.user.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        """
        Ensure we can delete a user.
        """
        response = self.client.delete(
            reverse("accounts:users-detail", args=[self.user.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password(self):
        """
        Ensure we can change password.
        """
        data = {
            "old_password": "testpassword",
            "new_password": "testpassword2",
        }
        response = self.client.post(reverse("accounts:users-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password_with_wrong_old_password(self):
        """
        Ensure we can change password.
        """
        data = {
            "old_password": "testpassword2",
            "new_password": "testpassword3",
        }
        response = self.client.post(reverse("accounts:users-change-password"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
