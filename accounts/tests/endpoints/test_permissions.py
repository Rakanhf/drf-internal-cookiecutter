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


class TestPermissionEndpoint(APITestCase):
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

    def test_get_permission_list(self):
        """
        Ensure we can get list of permissions.
        """
        response = self.client.get(reverse("accounts:permissions-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_permission_detail(self):
        """
        Ensure we can get a permission detail.
        """
        response = self.client.get(reverse("accounts:permissions-detail", args=[37]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_permission(self):
        """
        Ensure we can't create a new permission.
        """
        response = self.client.post(
            reverse("accounts:permissions-list"), {"name": "testpermission"}
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_permission(self):
        """
        Ensure we can't update a permission.
        """
        response = self.client.put(
            reverse("accounts:permissions-detail", args=[self.group.id]),
            {"name": "testpermission"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_permission(self):
        """
        Ensure we can't delete a permission.
        """
        response = self.client.delete(
            reverse("accounts:permissions-detail", args=[self.group.id])
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
