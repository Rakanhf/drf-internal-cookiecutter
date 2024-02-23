# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from auditlog.models import LogEntry
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager, Group, Permission
from rest_framework import serializers

from core.helpers.email_utils import EmailHelper
from authentication.helpers.device_helper import get_device_classes
from core.models import UserDevice
from accounts.models import Profile
from core.serializers import DynamicFieldsSerializer


class UserSerializer(DynamicFieldsSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=True
    )
    user_permissions = serializers.ListSerializer(read_only=True, required=False, child=serializers.CharField())
    otp_devices = serializers.ListSerializer(read_only=True, required=False, child=serializers.CharField())

    class Meta:
        model = get_user_model()
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "is_superuser": {"read_only": True},
            "is_staff": {"write_only": True},
            "username": {"write_only": True, "required": False},
        }

    def validate(self, data):
        if self.instance:
            for field in ["password", "is_superuser", "is_staff", "username"]:
                if field in data:
                    raise serializers.ValidationError(
                        {field: f"Updating {field.replace('_', ' ')} is not allowed."}
                    )
        else:
            for field in ["password", "is_superuser", "is_staff", "username"]:
                if field in data:
                    raise serializers.ValidationError(
                        {field: f"{field.replace('_', ' ')} is not an allowed field."}
                    )
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        all_permissions = self.get_all_permissions(instance)
        representation["user_permissions"] = list(all_permissions)

        # Retrieve device classes from settings
        device_classes = get_device_classes()

        # Iterate over device classes and check if the user has a confirmed device
        confirmed_devices = []
        for device_type, model in device_classes.items():
            if model.objects.filter(user=instance, confirmed=True).exists():
                confirmed_devices.append(device_type)

        # Add confirmed devices to the representation
        representation["otp_devices"] = confirmed_devices
        return representation

    def get_all_permissions(self, instance):
        # Get permissions directly assigned to the user
        user_permissions = {
            permission.codename for permission in instance.user_permissions.all()
        }
        # Get permissions assigned to the user via their groups
        group_permissions = {
            permission.codename
            for group in instance.groups.all()
            for permission in group.permissions.all()
        }
        # Merge the two sets to get all unique permissions
        all_permissions = user_permissions | group_permissions
        return all_permissions

    def create(self, validated_data):
        auto_password = BaseUserManager.make_random_password(self, length=8)
        groups = validated_data.pop("groups")
        user = get_user_model().objects.create_user(
            password=auto_password, **validated_data
        )
        user.groups.set(groups)
        # Assuming you have your email utility function defined somewhere
        self.send_welcome_email(user, auto_password)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop("groups", None)
        if groups is not None:
            instance.groups.set(groups)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def send_welcome_email(self, user, password):
        EmailHelper(
            subject="Welcome to the platform",
            template_name="emails/welcome.html",
            context={
                "name": user.first_name + " " + user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "password": password,
            },
        ).send_email(user.email)


class ChangePasswordSerializer(serializers.Serializer):
    model = get_user_model()
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value


class GroupSerializer(DynamicFieldsSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["permissions"] = [
            permission.codename for permission in instance.permissions.all()
        ]
        return representation

    class Meta:
        model = Group
        fields = "__all__"


class PermissionSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class UserDeviceSerializer(DynamicFieldsSerializer):
    class Meta:
        model = UserDevice
        fields = "__all__"

    def validate(self, data):
        if self.instance:
            for field in ["user", "user_agent", "ip_address", "last_login"]:
                if field in data:
                    raise serializers.ValidationError(
                        {field: f"Updating {field.replace('_', ' ')} is not allowed."}
                    )
        return data


class LogsSerializer(DynamicFieldsSerializer):
    class Meta:
        model = LogEntry
        exclude = ("additional_data", "serialized_data")


class ProfileSerializer(DynamicFieldsSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"
