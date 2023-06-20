# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from rest_framework import routers

from accounts.views import (
    GroupsViewSet,
    LogsViewSet,
    PermissionViewSet,
    UserDeviceViewSet,
    UsersViewSet,
)

router = routers.DefaultRouter()

router.register(r"users", UsersViewSet, basename="users")
router.register(r"groups", GroupsViewSet, basename="groups")
router.register(r"permissions", PermissionViewSet, basename="permissions")
router.register(r"devices", UserDeviceViewSet, basename="users_devices")
router.register(r"logs", LogsViewSet, basename="logs")

urlpatterns = router.urls
