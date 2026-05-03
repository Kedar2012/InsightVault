from django.contrib import admin
from .models import FraudFlag

# Register your models here.

@admin.register(FraudFlag)
class FraudFlagAdmin(admin.ModelAdmin):
    list_display = ("linked_object", "reason", "severity", "flagged_at", "resolved", "resolved_reason", "resolved_by")
    list_filter = ("severity", "resolved")

    def linked_object(self, obj):
        if obj.transaction:
            return f"Debit Tx {obj.transaction.id} - {obj.transaction.account}"
        elif obj.credit_request:
            return f"CreditRequest {obj.credit_request.id} - {obj.credit_request.account}"
        return "Unlinked"
    linked_object.short_description = "Linked Object"
    
# @admin.register(FraudEventLog)
# class FraudEventLogAdmin(admin.ModelAdmin):
#     list_display = ['user','event_type','details','created_at']

