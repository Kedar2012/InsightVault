from django.contrib import admin
from .models import Account, Transaction, FraudFlag

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user','account_number','balance']
    

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account','amount','transaction_type']
    

@admin.register(FraudFlag)
class FraudFlagAdmin(admin.ModelAdmin):
    list_display = ['transaction','reason','flagged_at']

