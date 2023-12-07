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


class TestGroupEndpoint(APITestCase):
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

    def test_get_group_list(self):
        """
        Ensure we can get list of groups.
        """
        response = self.client.get(reverse("accounts:groups-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_detail(self):
        """
        Ensure we can get a group detail.
        """
        response = self.client.get(
            reverse("accounts:groups-detail", args=[self.group.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_group(self):
        """
        Ensure we can create a new group.
        """

        data = {
            "name": "testgroup3",
            "permissions": [
                1,
                2,
                3,
            ],
        }
        response = self.client.post(reverse("accounts:groups-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_group(self):
        """
        Ensure we can update a group.
        """
        data = {
            "name": "testgroup3-updated",
            "permissions": [
                1,
                2,
                3,
            ],
        }
        response = self.client.put(
            reverse("accounts:groups-detail", args=[self.group.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_group(self):
        """
        Ensure we can delete a group.
        """
        response = self.client.delete(
            reverse("accounts:groups-detail", args=[self.group.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_permission_to_group(self):
        """
        Ensure we can add a permission to a group.
        """
        data = {
            "permissions": [
                1,
                2,
                3,
                4,
            ],
        }
        response = self.client.patch(
            reverse("accounts:groups-detail", args=[self.group.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_groups_me(self):
        """
        Ensure we can get list of groups for the requester.
        """
        response = self.client.get(reverse("accounts:groups-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
