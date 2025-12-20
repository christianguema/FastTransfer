from django.contrib import admin
from userauths.models import User, OPT

class AdminUser(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "gender",
        "phone"
    ]

class adminOPT(admin.ModelAdmin):
    list_display = [
        "code",
        "is_expire",
        "expire_at"
    ]
admin.site.register(User, AdminUser)
admin.site.register(OPT, adminOPT)