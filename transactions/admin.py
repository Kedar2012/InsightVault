from django.contrib import admin
from .models import Account, DebitTransaction

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user','account_number','balance']
    

@admin.register(DebitTransaction)
class DebitTransactionAdmin(admin.ModelAdmin):
    list_display = ['account','amount','status']

