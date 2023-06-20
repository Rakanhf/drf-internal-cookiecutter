# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from authentication.helpers.login_helper import LogUserDevice


class LogUserDeviceTest(TestCase):
    @patch("core.models.UserDevice.objects.get_or_create", return_value=(Mock(), True))
    @patch("core.helpers.email_utils.EmailHelper")
    @patch("core.helpers.email_utils.EmailHelper.send_email")
    def test_log_device_on_login(
        self, mock_email_helper_class, mock_email_send, mock_get_or_create
    ):
        # Create a test user
        user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass",
            first_name="Test",
            last_name="User",
        )

        # Create a mock request with RequestFactory
        factory = RequestFactory()
        mock_request = factory.get("/")
        mock_request.META["HTTP_USER_AGENT"] = "Other / Other / Other"
        mock_request.META["HTTP_X_FORWARDED_FOR"] = "127.0.0.1"

        # Create a LogUserDevice instance
        log_user_device = LogUserDevice(user, mock_request)

        # Call log_device_on_login
        log_user_device.log_device_on_login()

        # Check if get_or_create was called on UserDevice
        mock_get_or_create.assert_called_once_with(
            user=user,
            user_agent="Other / Other / Other",
            ip_address="127.0.0.1",
        )
