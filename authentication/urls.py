# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.urls import include, path
from core.schema import tag_view
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from authentication.views import (
    CustomTokenObtainPairView,
    OTPDisableView,
    OTPHandleRequestView,
    OTPResendView,
    OTPSetupView,
    OTPVerifyView,
    TokenOTPObtainPairView,
)

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "token/refresh/",
        tag_view(TokenRefreshView, "Token").as_view(),
        name="token_refresh",
    ),
    path(
        "token/verify/",
        tag_view(TokenVerifyView, "Token").as_view(),
        name="token_verify",
    ),
    path("2fa/activate/", OTPSetupView.as_view(), name="2fa_activate"),
    path("2fa/disable/", OTPDisableView.as_view(), name="2fa_disable"),
    path("2fa/verify/", OTPVerifyView.as_view(), name="2fa_verify"),
    path("2fa/resend/", OTPResendView.as_view(), name="2fa_resend"),
    path("token/2fa/", TokenOTPObtainPairView.as_view(), name="token_otp_obtain_pair"),
    path("2fa/challenge/", OTPHandleRequestView.as_view(), name="2fa_challenge"),
    path(
        r"reset-password/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
]
