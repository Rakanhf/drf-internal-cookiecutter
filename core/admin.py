from django.contrib import admin
from core.models import User, Profile

# Custom Admin Classes (Optional)
class UserAdmin(admin.ModelAdmin):
    # ... Customization here, e.g., fields to display ...
    pass

class ProfileAPIAdmin(admin.ModelAdmin):
     # ... Customization here, e.g., inlines for related data ...
    pass

# Register models 
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAPIAdmin)