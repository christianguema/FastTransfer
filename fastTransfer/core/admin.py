from django.contrib import admin
from core.models import TypeTransaction, TransactionStatus, Transactions, AccountOwner, Platform, VirtualAccount

class AdminTypeTransaction(admin.ModelAdmin):
    pass