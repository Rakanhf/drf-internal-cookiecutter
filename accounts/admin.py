# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.contrib import admin
from accounts.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileAPIAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'city', 'occupation', 'bio')
    search_fields = ('user__username', 'user__email', 'city')
    list_filter = ('country', 'occupation')
    readonly_fields = ('user',)

    fieldsets = (
        (None, {'fields': ('user', 'header_image')}),
        (
            'Location',
            {'fields': ('country', 'city', 'state', 'address', 'postal_code')},
        ),
        ('About', {'fields': ('bio', 'occupation')}),
    )


# Register models
admin.site.register(Profile, ProfileAPIAdmin)
