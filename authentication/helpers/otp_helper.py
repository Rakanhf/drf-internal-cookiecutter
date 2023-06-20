# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.apps import apps
from django.conf import settings
from django_user_agents.utils import get_user_agent
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from authentication.helpers.ip_utils import get_client_ip
from authentication.helpers.login_helper import LogUserDevice
from core.models import UserDevice


class OTPLoginFlowHelper:
    """
    Helper class to manage OTP (One Time Password) flow for a user.

    This class provides methods to start the OTP flow and handle an OTP request.
    It is initialized with a request, a user instance, and an optional method parameter.
    """

    def __init__(self, request, user, method=None):
        self.request = request
        self.user = user
        self.device_classes = {
            key: apps.get_model(val) for key, val in settings.OTP_DEVICE_CLASSES.items()
        }
        self.method = method

    def start_otp_flow(self):
        """
        Starts the OTP flow.

        This method checks if the user has enabled 2FA and if the
        user's device is trusted.

        If the user has enabled 2FA and the device is not trusted
        it generates a temporary token for the user

        and returns a response containing the temporary token and
        the available OTP devices.

        Returns:
            A Response containing a message indicating that 2FA is
            enabled, the default OTP method, the temporary token
            and the available OTP devices. If the user has not enabled 2FA
            or does not have a default OTP method, it returns None.
        """

        LogUserDevice(self.user, self.request).log_device_on_login()
        if not self.user.enabled_2fa or not self.user.default_2fa_method:
            return None

        if UserDevice.objects.filter(
            user=self.user,
            user_agent=get_user_agent(self.request),
            ip_address=get_client_ip(self.request),
            trusted=True,
        ).exists():
            return None

        temp_token = self.user.generate_temporary_token()

        devices = {
            method: cls.objects.get(user=self.user).id
            for method, cls in self.device_classes.items()
            if cls.objects.filter(user=self.user).exists()
        }

        return Response(
            {
                "message": "2FA is enabled for this user.",
                "default": self.user.default_2fa_method,
                "token": temp_token,
                "devices": devices,
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def handle_otp_request(self, device_id):
        """
        Handles an OTP request.

        This method receives a device id and generates an OTP
        challenge for the device.
        It then returns a response indicating that the challenge
        has been generated.

        Args:
            device_id: The id of the device that the OTP request is for.

        Returns:
            A Response containing a message indicating that the challenge
            has been generated, the id of the device, and the OTP method.
        """

        device_class = self.device_classes.get(self.method)
        if not device_class:
            raise ValidationError({"error": "Invalid 2FA type."})

        try:
            device = device_class.objects.get(user=self.user, id=device_id)
        except device_class.DoesNotExist:
            raise ValidationError(
                {"error": f"{self.method.upper()} device not found for this user."}
            )

        device.generate_challenge()

        return Response(
            {
                "message": f"Challenge generated for {self.method} device.",
                "device_id": device.id,
                "type": self.method,
            },
            status=status.HTTP_200_OK,
        )
