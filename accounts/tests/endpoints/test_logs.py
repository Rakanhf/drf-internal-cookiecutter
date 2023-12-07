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
from auditlog.models import LogEntry
from django.contrib.auth.models import Permission


class TestLogsEndpoint(APITestCase):
    def setUp(self):
        # This method will run before any test.

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser2@test.com",
            password="testpassword",
            phone_number="+905000000000",
            is_superuser=True,
        )
        self.user2 = get_user_model().objects.create_user(
            email="testuser3@test.com",
            password="testpassword",
            phone_number="+905000000001",
        )
        self.log_entry = LogEntry.objects.create(
            actor_id=self.user.id,
            content_type_id=1,  # This needs to be a valid ContentType id
            object_id="1",
            object_repr="Test Object",
            action=1,  # This needs to be a valid LogEntry action
        )
        self.log_entry2 = LogEntry.objects.create(
            actor_id=self.user2.id,
            content_type_id=1,  # This needs to be a valid ContentType id
            object_id="1",
            object_repr="Test Object",
            action=1,  # This needs to be a valid LogEntry action
        )
        refresh = RefreshToken.for_user(self.user)
        view_logentry_permission = Permission.objects.get(
            codename="view_logentry", content_type__app_label="auditlog"
        )
        self.user2.user_permissions.add(view_logentry_permission)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_log_list(self):
        """
        Ensure we can get list of logs for the authenticated user.
        """
        response = self.client.get(reverse("accounts:logs-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_log(self):
        """
        Ensure we can't create a new log.
        """
        response = self.client.post(reverse("accounts:logs-list"), {"name": "testlog"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_log_list_for_non_superuser(self):
        """self.assertEqual(response.status_code, status.HTTP_200_OK)er and it only includes logs associated with that user."""
        # Log in as user2
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        response = self.client.get(reverse("accounts:logs-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_log(self):
        """
        Ensure we can't update a log.
        """
        response = self.client.put(
            reverse("accounts:logs-detail", args=[self.log_entry.id]),
            {"name": "testlog"},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_log(self):
        """
        Ensure we can't delete a log.
        """
        response = self.client.delete(
            reverse("accounts:logs-detail", args=[self.log_entry.id])
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_log_me(self):
        """
        Ensure we can get a log detail for the authenticated user.
        """
        response = self.client.get(reverse("accounts:logs-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
