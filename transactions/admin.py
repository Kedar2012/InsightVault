from django.contrib import admin
from .models import Account, DebitTransaction, CreditRequest, CreditTransaction, ManualDebitTransaction, ReversalTransaction

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user','account_number','balance']

@admin.register(DebitTransaction)
class DebitTransactionAdmin(admin.ModelAdmin):
    list_display = ['account','amount','description','status']

@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "deposit_reference", "status", "created_at")

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "deposit_reference", "status", "timestamp")

@admin.register(ManualDebitTransaction)
class ManualDebitTransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "reason", "created_by", "status", "is_global")

@admin.register(ReversalTransaction)
class ReversalTransactionAdmin(admin.ModelAdmin):
    list_display = ("linked_object", "account", "amount", "reason", "created_by", "status")

    def linked_object(self, obj):
        if obj.debit_transaction:
            return f"Debit Tx {obj.debit_transaction.id} - {obj.debit_transaction.account}"
        elif obj.credit_transaction:
            return f"Debit Tx {obj.credit_transaction.id} - {obj.credit_transaction.account}"
        elif obj.manual_debit_transaction:
            return f"Debit Tx {obj.manual_debit_transaction.id} - {obj.manual_debit_transaction.account}"
        return "Unlinked"
    linked_object.short_description = "Linked Object"