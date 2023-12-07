# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from django.db import models
from core.validators import validate_image_file_extension
from django.utils.translation import gettext as _
from auditlog.registry import auditlog
from auditlog.context import disable_auditlog


class Profile(models.Model):
    user = models.OneToOneField(
        "core.User", on_delete=models.CASCADE, related_name="profile"
    )
    header_image = models.ImageField(
        default="header/default.png",
        upload_to="header/",
        validators=[validate_image_file_extension],
    )
    country = models.CharField(max_length=50, null=True, default=None)
    city = models.CharField(max_length=50, null=True, default=None)
    state = models.CharField(max_length=50, null=True, default=None)
    address = models.CharField(max_length=240, null=True, default=None)
    postal_code = models.CharField(max_length=50, null=True, default=None)
    bio = models.TextField(max_length=5000, null=True, default=None)
    occupation = models.CharField(max_length=50, null=True, default=None)

    def delete(self, *args, **kwargs):
        with disable_auditlog():
            super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        ordering = ["-id"]


auditlog.register(Profile)
