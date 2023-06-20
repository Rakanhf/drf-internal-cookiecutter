# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from auditlog.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django_user_agents.utils import get_user_agent
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.serializers import (
    ChangePasswordSerializer,
    GroupSerializer,
    LogsSerializer,
    PermissionSerializer,
    UserDeviceSerializer,
    UserSerializer,
)
from authentication.helpers.ip_utils import get_client_ip
from core.helpers.email_utils import EmailHelper
from core.models import UserDevice
from core.pagination import GlobalPagination
from core.permissions import IsSuperUserOrDjangoModelPermissions
from core.views import DynamicFieldsModelViewSet, ListUpdateViewSet

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType


class UsersViewSet(DynamicFieldsModelViewSet):
    """
    Endpoint:
    =========
    GET /users
    GET /users/me
    POST /users/
    POST /users/change_password/
    PUT /users/<id>/
    PATCH /users/<id>/
    DELETE /users/<id>/
    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    filterset_fields = ["first_name", "last_name", "email", "phone_number", "is_active"]
    search_fields = ["first_name", "last_name", "email", "phone_number"]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        This custom action returns the user data for the requester.
        """
        serializer = super().get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """
        This custom action updates the password for the requester.
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.data.get("old_password")):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.data["new_password"])
        user.save()
        EmailHelper(
            subject="Password changed",
            template_name="emails/password_changed.html",
            context={
                "name": user.first_name + " " + user.last_name,
                "ip": get_client_ip(request)[0],
                "user_agent": get_user_agent(request),
                "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        ).send_email(user.email)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupsViewSet(DynamicFieldsModelViewSet):
    """
    Endpoint:
    =========
    GET /groups
    POST /groups/
    PUT /groups/<id>/
    PATCH /groups/<id>/
    DELETE /groups/<id>/
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filterset_fields = ["name"]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint:
    =========
    GET /permissions
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperUserOrDjangoModelPermissions]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        # Define the models to exclude
        models_to_exclude = [
            ("admin", "logentry"),
            ("contenttypes", "contenttype"),
            ("sessions", "session"),
            ("otp_totp", "totpdevice"),
            ("otp_email", "emaildevice"),
            ("phonenumber", "phonedevice"),
            ("django_rest_passwordreset", "passwordresettoken"),
            ("core", "expiringtoken"),
            ("authentication", "customemaildevice"),
        ]

        # Create Q objects for all models to exclude
        q_objects = Q()
        for app_label, model in models_to_exclude:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                q_objects |= Q(content_type=content_type)
            except ContentType.DoesNotExist:
                print(f"No ContentType exists for app: '{app_label}' model: '{model}'")

        # Exclude all permissions related to these content types
        return Permission.objects.exclude(q_objects)


class UserDeviceViewSet(ListUpdateViewSet):
    """
    Endpoint:
    =========
    GET /devices
    PUT /devices/<id>/
    PATCH /devices/<id>/
    DELETE /devices/<id>/
    """

    serializer_class = UserDeviceSerializer

    def get_queryset(self):
        return UserDevice.objects.filter(user=self.request.user).order_by("-last_login")


class LogsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint:
    =========
    GET /logs
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperUserOrDjangoModelPermissions]
    queryset = LogEntry.objects.all()
    pagination_class = GlobalPagination
    serializer_class = LogsSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return LogEntry.objects.all().order_by("-timestamp")
        return LogEntry.objects.filter(actor=self.request.user).order_by("-timestamp")
