# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from accounts.serializers import UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email_or_phone_number = attrs.get("email")
        user = (
            get_user_model()
            .objects.filter(
                Q(email=email_or_phone_number) | Q(phone_number=email_or_phone_number)
            )
            .first()
        )

        if user:
            attrs["email"] = user.email

        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        data["header_types"] = settings.SIMPLE_JWT["AUTH_HEADER_TYPES"]
        data["refresh_expires"] = refresh.access_token.payload["exp"]
        data["access_expires"] = refresh.payload["exp"]
        data["user"] = UserSerializer(self.user).data

        return data


class CustomTokenObtainPairResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    header_types = serializers.CharField()
    refresh_expires = serializers.IntegerField()
    access_expires = serializers.IntegerField()
    user = UserSerializer()


class CustomTokenObtainPairResponse2FASerializer(serializers.Serializer):
    message = serializers.CharField()
    default = serializers.CharField()
    token = serializers.CharField()
    devices = serializers.DictField(child=serializers.IntegerField())


class TokenOTPObtainPairSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=True)
    token = serializers.CharField(required=True)
    type = serializers.CharField(required=True)


class TokenOTPObtainPairResponseSerializer(CustomTokenObtainPairResponseSerializer):
    user_device_id = serializers.CharField()


class OTPHandleRequestSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(required=True)
    token = serializers.CharField(required=True)


class OTPHandleRequestResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    device_id = serializers.IntegerField()
    type = serializers.CharField()


class OTPSetupViewSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)


class OTPSetupViewResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    device_id = serializers.IntegerField()
    method = serializers.CharField()
    qr_data = serializers.CharField()


class OTPDisableViewResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class OTPResendViewSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    device_id = serializers.IntegerField(required=True)


class OTPDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    name = serializers.CharField(max_length=100)
    confirmed = serializers.BooleanField()
