# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from django.test import TestCase, RequestFactory
from authentication.helpers.ip_utils import get_client_ip


class GetClientIPTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_ip_from_remote_addr(self):
        # Create a request object with a REMOTE_ADDR value
        request = self.factory.get("/", REMOTE_ADDR="192.168.0.1")

        # Call your function with the request
        ip = get_client_ip(request)

        # Check that the function correctly extracted the IP
        self.assertEqual(ip, "192.168.0.1")

    def test_get_ip_from_x_forwarded_for(self):
        # Create a request object with a HTTP_X_FORWARDED_FOR value
        request = self.factory.get("/", HTTP_X_FORWARDED_FOR="192.168.0.2, 192.168.0.3")

        # Call your function with the request
        ip = get_client_ip(request)

        # Check that the function correctly extracted the first IP
        self.assertEqual(ip, "192.168.0.2")
