# Project: drf-internal-cookiecutter
#       |\      _,,,---,,_
# ZZZzz /,`.-'`'    -.  ;-;;,_
#      |,4-  ) )-,_. ,\ (  `'-'
#     '---''(_/--'  `-'\_)
#           @Rakanhf
#           Rakan Farhouda
#


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from core.models import User, UserDevice

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone_number', 'is_staff', 'is_active', 'enabled_2fa')
    search_fields = ('email', 'phone_number', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'enabled_2fa', 'last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Keep important fields at the top
        ('Personal Info', {'fields': ('phone_number', 'avatar', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}), 
        ('2FA', {'fields': ('enabled_2fa', 'default_2fa_method')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ('last_login', 'date_joined')  # Informational fields



class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_agent', 'ip_address', 'last_login', 'trusted')
    search_fields = ('user__email', 'user_agent', 'ip_address')
    list_filter = ('trusted',)
    readonly_fields = ('user', 'user_agent', 'ip_address', 'last_login')


# Register models 
admin.site.register(User, UserAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)