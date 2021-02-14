from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from users.models import Profile


# Register your models here.
"""class CustomUserInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (CustomUserInline,)"""


admin.site.register(Profile)
#admin.site.register(User, UserAdmin)
