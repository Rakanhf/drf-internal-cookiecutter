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
from accounts.serializers import UserSerializer
from core.models import User
from rest_framework import serializers


class TestUserSerializer(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(name="Test Group")
        self.user = User.objects.create_user(
            email="username@test.com",
            phone_number="+905123456714",
        )
        self.user.groups.set([self.group])
        self.client = APIClient()
        self.serializer = UserSerializer(instance=self.user)

    def test_to_representation(self):
        serializer = UserSerializer(self.user, context={"fields": ["user_permissions"]})
        data = serializer.data
        self.assertIn("user_permissions", data)
        self.assertEqual(data["user_permissions"], [])

    def test_create_without_group(self):
        data = {"email": "testuser@test.com", "phone_number": "+905123456715"}
        serializer = UserSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_create_with_invalid_group(self):
        data = {
            "email": "testuser@test.com",
            "phone_number": "+905123456716",
            "groups": [9999],  # Invalid group id
        }
        serializer = UserSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    @patch("core.helpers.email_utils.EmailHelper.send_email")
    def test_create_with_group(self, MockEmailHelper):
        data = {
            "email": "testuser@test.com",
            "phone_number": "+905123456718",
            "groups": [self.group.id],
        }
        serializer = UserSerializer(data=data)

        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertEqual(user.groups.first(), self.group)
        MockEmailHelper.assert_called()

    def test_update(self):
        another_group = Group.objects.create(name="Another Test Group")

        data = {"email": "updated@test.com", "groups": [another_group.id]}
        serializer = UserSerializer(instance=self.user, data=data, partial=True)

        self.assertTrue(serializer.is_valid(raise_exception=True))
        user = serializer.save()
        self.assertEqual(user.groups.first(), another_group)
