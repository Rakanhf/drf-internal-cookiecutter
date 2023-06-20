# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.conf import settings
from django_otp.plugins.otp_email.models import EmailDevice as DefaultEmailDevice

from core.helpers.email_utils import EmailHelper


class CustomEmailDevice(DefaultEmailDevice):
    def generate_challenge(self, extra_context=None):
        """
        Generates a random token and emails it to the user.

        :param extra_context: Additional context variables for rendering the
            email template.
        :type extra_context: dict

        """
        self.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)

        subject = settings.OTP_EMAIL_SUBJECT
        template_name = settings.OTP_EMAIL_BODY_TEMPLATE
        context = {"token": self.token}
        to_email = self.user.email
        email_helper = EmailHelper(subject, template_name, context)
        email_helper.send_email(to_email)

        message = "sent by email"

        return message
