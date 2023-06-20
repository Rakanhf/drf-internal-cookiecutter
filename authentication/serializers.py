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
