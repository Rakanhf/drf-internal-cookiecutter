# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.conf import settings
from django.template.loader import render_to_string
from two_factor.gateways.twilio.gateway import Twilio


class CustomTwilioGateWay(Twilio):
    def send_sms(self, device, token):
        """
        send sms using template from settings OTP_SMS_BODY_TEMPLATE
        """
        body = render_to_string(settings.OTP_SMS_BODY_TEMPLATE, {"token": token})
        send_kwargs = {"to": device.number.as_e164, "body": body}
        messaging_service_sid = getattr(settings, "TWILIO_MESSAGING_SERVICE_SID", None)
        if messaging_service_sid is not None:
            send_kwargs["messaging_service_sid"] = messaging_service_sid
        else:
            send_kwargs["from_"] = getattr(settings, "TWILIO_CALLER_ID")

        self.client.messages.create(**send_kwargs)
