# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#

from django.contrib import admin
from authentication.models import CustomEmailDevice


# Custom Admin Classes (Optional)
class CustomEmailDeviceAdmin(admin.ModelAdmin):
    # ... Customization here, e.g., fields to display ...
    pass


# Register models
admin.site.register(CustomEmailDevice, CustomEmailDeviceAdmin)
