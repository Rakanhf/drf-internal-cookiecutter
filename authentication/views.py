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
from django.contrib.auth import get_user_model
from django_user_agents.utils import get_user_agent
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import UserSerializer
from authentication.backends import TemporaryTokenAuthentication
from authentication.helpers.ip_utils import get_client_ip
from authentication.helpers.otp_helper import OTPLoginFlowHelper
from authentication.throttling import LoginThrottle
from core.models import UserDevice


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    *Handles token operations for API authentication.*
    Custom view to handle token pair creation with additional OTP flow for user authentication.

    Throttle login attempts to prevent brute-force attacks.
    """

    throttle_classes = [LoginThrottle]
    drf_tag = "Login"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = get_user_model().objects.get(
                pk=serializer.validated_data["user"]["id"]
            )
            response = OTPLoginFlowHelper(request, user).start_otp_flow()
            if response:
                return response
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user_device_id = (
            UserDevice.objects.filter(
                user=user,
                user_agent=get_user_agent(request),
                ip_address=get_client_ip(request),
                trusted=False,
            )
            .order_by("-last_login")
            .values_list("id", flat=True)
            .first()
        )

        if user_device_id:
            serializer.validated_data["user_device_id"] = user_device_id

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class OTPBaseView(generics.GenericAPIView):
    """
    Base view for handling OTP (One Time Password) functionalities.

    This view provides common methods for OTP handling including device verification
    and token validation. Specific OTP handling behavior should be implemented in subclasses
    by overriding `handle_valid_otp` method.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    device_classes = {
        key: apps.get_model(val) for key, val in settings.OTP_DEVICE_CLASSES.items()
    }
    drf_tag = "Auth"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.otp_type = None

    def get_device(self, user, device_id):
        device_class = self.device_classes.get(self.otp_type)

        if not device_class:
            raise ValidationError({"error": "Invalid 2FA type."})

        try:
            device = device_class.objects.get(user=user, id=device_id)
        except device_class.DoesNotExist:
            raise ValidationError(
                {"error": f"{self.otp_type.upper()} device not found for this user."}
            )

        return device

    def post(self, request, *args, **kwargs):
        user = request.user
        self.otp_type = request.data.get("type")
        token = request.data.get("token")
        device_id = request.data.get("device_id")

        if not self.otp_type or not token or not device_id:
            raise ValidationError(
                {"error": "Missing required parameters (type, token, device_id)."}
            )

        device = self.get_device(user, device_id)

        if not device.verify_token(token):
            raise ValidationError({"error": f"Invalid {self.otp_type.upper()} token."})

        return self.handle_valid_otp(user, device, request)

    def handle_valid_otp(self, user, device, request):
        raise NotImplementedError()


class TokenOTPObtainPairView(OTPBaseView):
    """
    *Handles token operations for API authentication.*
    Custom view to handle token pair creation upon successful OTP verification.

    Once OTP is validated, temporary token is deleted and a new token pair (refresh and access)
    is created for the user. The response includes the token pair along with additional user data.
    """

    authentication_classes = [TemporaryTokenAuthentication]
    drf_tag = "Login"

    def handle_valid_otp(self, user, device, request):
        user.delete_temporary_token()
        refresh = RefreshToken.for_user(user)
        user_device_id = (
            UserDevice.objects.filter(
                user=user,
                user_agent=get_user_agent(request),
                ip_address=get_client_ip(request),
                trusted=False,
            )
            .order_by("-last_login")
            .values_list("id", flat=True)
            .first()
        )
        # return the access and refresh token and the user object using UserSerializer
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "header_types": settings.SIMPLE_JWT["AUTH_HEADER_TYPES"],
            "refresh_expires": refresh.access_token.payload["exp"],
            "access_expires": refresh.payload["exp"],
            "user": UserSerializer(user).data,
        }
        if user_device_id:
            data["user_device_id"] = user_device_id
        return Response(data, status=status.HTTP_200_OK)


class OTPSetupView(OTPBaseView):
    """
    *Provides two-factor authentication settings and verification.*
    Custom view for initiating the OTP (One Time Password) setup process for a user.

    On successful POST, it creates or retrieves the OTP device associated with the user.
    If the device is not confirmed, it initiates the OTP setup process.
    """

    drf_tag = "Two Factor Authentication"

    def post(self, request, *args, **kwargs):
        user = request.user
        self.otp_type = request.data.get("type")

        if not self.otp_type:
            return Response(
                {"error": "Missing required parameters (type)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device_class = self.device_classes.get(self.otp_type)
        if not device_class:
            return Response(
                {"error": "Invalid 2FA type."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            device = device_class.objects.get(user=user)
            if device.confirmed:
                raise ValidationError(
                    {
                        "error": f"{self.otp_type.upper()} 2FA is already enabled for this user."
                    }
                )
        except device_class.DoesNotExist:
            device = device_class.objects.create(user=user, confirmed=False)

        if self.otp_type == "sms":
            device.number = user.phone_number
            device.save()

        return self.handle_valid_otp(user, device, request)

    def handle_valid_otp(self, user, device, request):
        device.confirmed = False
        device.save()
        device.generate_challenge()
        if self.otp_type == "totp":
            qr_data = device.config_url
        return Response(
            {
                "message": f"{self.otp_type.upper()} 2FA setup initiated.",
                "device_id": device.id,
                "method": self.otp_type,
                "qr_data": qr_data if self.otp_type == "totp" else None,
            },
            status=status.HTTP_200_OK,
        )


class OTPVerifyView(OTPBaseView):
    """
    *Provides two-factor authentication settings and verification.*
    Custom view for handling OTP (One Time Password) verification.

    On a valid OTP, the associated device is confirmed and OTP for the user is enabled.
    """

    drf_tag = "Two Factor Authentication"

    def handle_valid_otp(self, user, device, request):
        if device.confirmed:
            raise ValidationError(
                {
                    "error": f"{self.otp_type.upper()} 2FA is already enabled for this user."
                }
            )

        device.confirmed = True
        device.save()

        if not user.default_2fa_method:
            user.default_2fa_method = self.otp_type

        if not user.enabled_2fa:
            user.enabled_2fa = True
            user.save()

        return Response(
            {"message": f"{self.otp_type.upper()} 2FA verified and enabled."},
            status=status.HTTP_200_OK,
        )


class OTPResendView(OTPBaseView):
    """
    *Provides two-factor authentication settings and verification.*
    Custom view for handling OTP (One Time Password) resend requests.

    If the associated device is not confirmed, a new OTP challenge is generated.
    """

    drf_tag = "Two Factor Authentication"

    def post(self, request, *args, **kwargs):
        user = request.user
        self.otp_type = request.data.get("type")
        device_id = request.data.get("device_id")

        if not self.otp_type or not device_id:
            raise ValidationError(
                {"error": "Missing required parameters (type, device_id)."}
            )

        device = self.get_device(user, device_id)

        return self.handle_valid_otp(user, device, request)

    def handle_valid_otp(self, user, device, request):
        if device.confirmed:
            raise ValidationError(
                {"error": "Invalid device ID or 2FA is already enabled."}
            )

        device.generate_challenge()
        return Response(
            {"message": f"{self.otp_type.upper()} 2FA code resent."},
            status=status.HTTP_200_OK,
        )


class OTPHandleRequestView(OTPBaseView):
    """
    *Handles token operations for API authentication.*
    Custom view for handling OTP request after initiating the OTP flow.

    This view receives the device id and type from the client,
    generates the OTP challenge and logs the user device.
    """

    drf_tag = "Login"

    authentication_classes = [TemporaryTokenAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user
        device_id = request.data.get("device_id")
        otp_type = request.data.get("type")

        if not otp_type or not device_id:
            raise ValidationError(
                {"error": "Missing required parameters (type, device_id)."}
            )

        otp_helper = OTPLoginFlowHelper(request, user, otp_type)
        response = otp_helper.handle_otp_request(device_id)

        return response


class OTPDisableView(OTPBaseView):
    """
    *Provides two-factor authentication settings and verification.*
    Custom view for disabling the OTP (One Time Password) for a user.

    On successful POST, it finds and deletes the OTP device associated with the user.
    It also updates the user's 2FA fields.
    """

    drf_tag = "Two Factor Authentication"

    def post(self, request, *args, **kwargs):
        user = request.user
        self.otp_type = request.data.get("type")

        if not self.otp_type:
            return Response(
                {"error": "Missing required parameters (type)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.otp_type == "all":
            self.disable_all_2fa(user)
        else:
            self.disable_specific_2fa(user, self.otp_type)

        return Response(
            {"message": "2FA has been disabled."}, status=status.HTTP_200_OK
        )

    def disable_all_2fa(self, user):
        for otp_type in self.device_classes.keys():
            self.disable_specific_2fa(user, otp_type)

        user.enabled_2fa = False
        user.default_2fa_method = None
        user.save()

    def disable_specific_2fa(self, user, otp_type):
        device_class = self.device_classes.get(otp_type)
        if not device_class:
            raise ValidationError({"error": "Invalid 2FA type."})

        try:
            device = device_class.objects.get(user=user)
            device.delete()
        except device_class.DoesNotExist:
            pass

        if user.default_2fa_method == otp_type:
            user.default_2fa_method = None
            user.save()

        if not self.user_has_devices(user):
            user.enabled_2fa = False
            user.save()

    def user_has_devices(self, user):
        for device_class in self.device_classes.values():
            if device_class.objects.filter(user=user).exists():
                return True
        return False
