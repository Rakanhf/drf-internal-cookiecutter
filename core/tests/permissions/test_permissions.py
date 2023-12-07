from django.test import TestCase
from django.contrib.auth.models import Permission, Group
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAndProfilePermissionTests(TestCase):
    def setUp(self):
        # Create test users
        self.superuser = User.objects.create_superuser(
            email="superuser@test.com",
            password="superpassword",
            phone_number="1234567890",
        )
        self.regular_user = User.objects.create_user(
            email="regularuser@test.com",
            password="regularpassword",
            phone_number="1234567891",
        )
        self.other_user = User.objects.create_user(
            email="otheruser@test.com",
            password="otherpassword",
            phone_number="1234567892",
        )

        # Assign permissions to the regular user
        permission_view = Permission.objects.get(codename="view_user")
        permission_add = Permission.objects.get(codename="add_user")
        permission_delete = Permission.objects.get(codename="delete_user")
        # create a group
        group = Group.objects.create(name="testgroup")
        # add permissions to the group
        group.permissions.set([permission_view, permission_add, permission_delete])
        # assign the group to the regular user
        self.regular_user.groups.add(group)

        # Setting up the API client
        self.client = APIClient()

    def test_me_endpoint_access(self):
        # Users should be able to access the /me endpoint without additional permissions
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(
            reverse("accounts:users-me")
        )  # Assuming 'users-me' is the name of the URL pattern
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_access_with_permission(self):
        # Regular user with view permission should have access to the user list
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(
            reverse("accounts:users-list")
        )  # Adjust 'accounts:users-list' as needed
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_access_without_permission(self):
        # Other user without view permission should not have access to the user list
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse("accounts:users-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_with_permission(self):
        # Regular user with add permission should be able to create a new user
        self.client.force_authenticate(user=self.regular_user)
        data = {
            "email": "testuser2@test.com",
            "phone_number": "+905123456715",
            "groups": [],
        }
        response = self.client.post(reverse("accounts:users-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_delete_with_permission(self):
        # Regular user with delete permission should be able to delete a user
        user_to_delete = User.objects.create_user(
            email="deleteuser@test.com",
            password="deletepassword",
            phone_number="+905444477665",
        )
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(
            reverse("accounts:users-detail", kwargs={"pk": user_to_delete.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
