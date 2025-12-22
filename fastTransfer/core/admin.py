from django.contrib import admin
from core.models import Transactions, AccountOwner, Platform, VirtualAccount

class AdminTransaction(admin.ModelAdmin):
    list_display = ["reference","types","amount","fee","net_amount","status","sender_account","receiver_account"]


class AdminAccountOwner(admin.ModelAdmin):
    list_display=["owner"]


class AdminVitualAccount(admin.ModelAdmin):
    list_display= ["balance","is_active","owner"]


class AdminPlateform(admin.ModelAdmin):
    list_display=["name", "withdrawal_fee_rate"]


admin.site.register(Transactions, AdminTransaction)
admin.site.register(VirtualAccount, AdminVitualAccount)
admin.site.register(AccountOwner, AdminAccountOwner)
admin.site.register(Platform, AdminPlateform)