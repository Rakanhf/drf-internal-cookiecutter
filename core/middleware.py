# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer"):
            # Extract token
            token = auth_header[7:]
            if len(token) != 40:  # Replace 40 with the actual length of your temp token
                try:
                    result = JWTAuthentication().authenticate(request)
                    if result is not None:
                        user, _ = result
                        request.user = user
                except Exception as e:
                    return JsonResponse(e.args[0], status=401)
        return self.get_response(request)
