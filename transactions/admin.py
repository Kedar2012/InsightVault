from django.contrib import admin
from .models import Account, DebitTransaction, CreditRequest, CreditTransaction

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user','account_number','balance']

@admin.register(DebitTransaction)
class DebitTransactionAdmin(admin.ModelAdmin):
    list_display = ['account','amount','status']

@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "deposit_reference", "status", "created_at")

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "deposit_reference", "status", "timestamp")

