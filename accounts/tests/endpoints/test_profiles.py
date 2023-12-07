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


class TestProfilesEndpoint(APITestCase):
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

    def test_get_profiles(self):
        # Test GET accounts/profiles/
        # Should return 200
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("accounts:profiles-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile(self):
        # Test GET accounts/profiles/{id}/
        # Should return 200
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("accounts:profiles-detail", args=[self.user.profile.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_not_found(self):
        # Test GET accounts/profiles/{id}/
        # Should return 404
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("accounts:profiles-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_profile(self):
        # Test POST accounts/profiles/
        # Should return 405 (Method Not Allowed)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("accounts:profiles-list"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        # Test PUT accounts/profiles/{id}/
        # Should return 200
        self.client.force_authenticate(user=self.user)
        response = self.client.put(
            reverse("accounts:profiles-detail", args=[self.user.profile.id]),
            data={
                # header_image file is not required
                "country": "Turkey",
                "city": "Istanbul",
                "state": "Istanbul",
                "address": "10.cd",
                "postal_code": "34451",
                "bio": "TEST",
                "occupation": "CEO",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_me(self):
        # Test GET accounts/profiles/me/
        # Should return 200
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("accounts:profiles-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
