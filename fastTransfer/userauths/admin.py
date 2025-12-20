from django.contrib import admin
from userauths.models import User

class AdminUser(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "gender",
        "phone"
    ]

admin.site.register(User, AdminUser)