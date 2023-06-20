# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from auditlog.registry import auditlog
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from auditlog.context import disable_auditlog

from core.validators import validate_image_file_extension


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


# Custom Abstract User with email as login field
class User(AbstractUser):
    username = models.CharField(max_length=100, unique=False, null=True, default=None)
    email = models.EmailField(
        verbose_name="email",
        max_length=75,
        unique=True,
    )
    phone_number = PhoneNumberField(unique=True)
    avatar = models.ImageField(
        default="avatar/default.png",
        upload_to="avatar/",
        validators=[validate_image_file_extension],
    )
    enabled_2fa = models.BooleanField(default=False)
    default_2fa_method = models.CharField(max_length=10, null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # removes email from REQUIRED_FIELDS

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def delete(self, *args, **kwargs):
        with disable_auditlog():
            super().delete(*args, **kwargs)

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        return "No Name"

    def generate_temporary_token(self):
        ExpiringToken.objects.filter(user=self).delete()
        token, _ = ExpiringToken.objects.get_or_create(user=self)
        return token.key

    def delete_temporary_token(self):
        ExpiringToken.objects.filter(user=self).delete()


auditlog.register(User, exclude_fields=["password"])


class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    last_login = models.DateTimeField(auto_now=True)
    trusted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "user_agent", "ip_address")


auditlog.register(UserDevice)


class ExpiringToken(models.Model):
    key = models.CharField("Key", max_length=40, primary_key=True)
    user = models.OneToOneField(
        User, related_name="expiring_token", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField("Created", auto_now_add=True)
    expires_at = models.DateTimeField("Expires")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_string(length=40)
        self.expires_at = timezone.now() + settings.TOKEN_EXPIRATION_TIME
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()
