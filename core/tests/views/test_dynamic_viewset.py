# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group


class DynamicFieldsModelViewSetTest(APITestCase):
    FIELDS = [
        "id",
        "groups",
        "last_login",
        "is_superuser",
        "first_name",
        "last_name",
        "is_active",
        "date_joined",
        "email",
        "phone_number",
        "avatar",
        "enabled_2fa",
        "default_2fa_method",
        "user_permissions",
    ]

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

    def test_specific_field(self):
        response = self.client.get(reverse("accounts:users-list") + "?fields=email")
        self.assertIn("email", response.data["results"][0])
        self.assertNotIn("phone_number", response.data["results"][0])

    def test_multiple_fields(self):
        response = self.client.get(
            reverse("accounts:users-list") + "?fields=email,phone_number"
        )
        self.assertIn("email", response.data["results"][0])
        self.assertIn("phone_number", response.data["results"][0])

    def test_invalid_field(self):
        response = self.client.get(
            reverse("accounts:users-list") + "?fields=invalid_field"
        )
        for field in DynamicFieldsModelViewSetTest.FIELDS:
            self.assertIn(field, response.data["results"][0])

    def test_empty_fields(self):
        response = self.client.get(reverse("accounts:users-list") + "?fields=")
        for field in DynamicFieldsModelViewSetTest.FIELDS:
            self.assertIn(field, response.data["results"][0])

    def test_one_valid_one_invalid_field(self):
        response = self.client.get(
            reverse("accounts:users-list") + "?fields=email,invalid_field"
        )
        self.assertIn("email", response.data["results"][0])
        self.assertNotIn("phone_number", response.data["results"][0])
