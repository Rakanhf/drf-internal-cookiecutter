# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch
from accounts.serializers import ProfileSerializer
from accounts.models import Profile
from rest_framework import serializers
from core.models import User


class TestProfileSerializer(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            phone_number="+905123456714",
        )
        self.client = APIClient()
        self.serializer = ProfileSerializer(instance=self.user.profile)

    def test_to_representation(self):
        serializer = ProfileSerializer(self.user.profile)
        data = serializer.data
        self.assertIn("user", data)
        self.assertEqual(data["user"], self.user.id)
