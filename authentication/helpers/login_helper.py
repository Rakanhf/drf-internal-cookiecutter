# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.utils import timezone
from django_user_agents.utils import get_user_agent

from authentication.helpers.ip_utils import get_client_ip
from core.helpers.email_utils import EmailHelper
from core.models import UserDevice


class LogUserDevice:
    def __init__(self, user, request):
        self.user = user
        self.request = request
        self.user_agent = get_user_agent(request)
        self.ip_address = get_client_ip(request)

    def log_device_on_login(self):
        user_device, created = UserDevice.objects.get_or_create(
            user=self.user,
            user_agent=str(self.user_agent),
            ip_address=self.ip_address,
        )

        if created:
            self.user.last_login = timezone.now()
            self.user.save()
            # Send a notification email to the user
            EmailHelper(
                subject="Unrecognized device login",
                template_name="emails/unrecognized_device_login.html",
                context={
                    "name": self.user.first_name + " " + self.user.last_name,
                    "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_agent": self.user_agent,
                    "ip": self.ip_address,
                },
            ).send_email(self.user.email)
        else:
            user_device.last_login = timezone.now()
            user_device.save()
