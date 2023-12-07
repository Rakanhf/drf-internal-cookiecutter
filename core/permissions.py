# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from rest_framework.permissions import DjangoModelPermissions
from rest_framework import permissions
from django.contrib.auth import get_user_model


class IsSuperUserOrDjangoModelPermissions(DjangoModelPermissions):
    """
    Allow full access if user is a superuser.
    Otherwise, use DjangoModelPermissions.
    """

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_superuser
            or super().has_permission(request, view)
        )


class DynamicAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Apply IsSuperUserOrDjangoModelPermissions globally
        if IsSuperUserOrDjangoModelPermissions().has_permission(request, view):
            return True

        # Strictly handle list requests
        if view.action == "list":
            # Deny access for list requests unless the user has specific permissions
            # You can customize this part based on your application's logic
            return False

        # For non-list actions, allow proceeding to object-level permission checks
        return True

    def has_object_permission(self, request, view, obj):
        # First, allow superusers unrestricted access
        if request.user and request.user.is_superuser:
            return True
        # Check for specific permissions for the action
        if IsSuperUserOrDjangoModelPermissions().has_object_permission(
            request, view, obj
        ):
            return True
        # Check if the user is trying to access their own information
        if isinstance(obj, get_user_model()):
            return obj == request.user
        if hasattr(
            obj, "user"
        ):  # For UserDevice, CustomEmailDevice, Profile, OTP Devices
            return obj.user == request.user
        # Default to False if none of the above conditions are met
        return False
