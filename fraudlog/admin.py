from django.contrib import admin
from .models import FraudFlag

# Register your models here.

@admin.register(FraudFlag)
class FraudFlagAdmin(admin.ModelAdmin):
    list_display = ['transaction','reason','flagged_at']
    
# @admin.register(FraudEventLog)
# class FraudEventLogAdmin(admin.ModelAdmin):
#     list_display = ['user','event_type','details','created_at']

