# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.conf import settings
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from core.helpers.email_utils import EmailHelper


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    email_plaintext_message = settings.RESET_PASSWORD_URL + reset_password_token.key
    EmailHelper(
        subject="Reset Password",
        template_name="emails/password_reset.html",
        context={
            "reset_password_url": email_plaintext_message,
        },
    ).send_email(to_email=reset_password_token.user.email)
