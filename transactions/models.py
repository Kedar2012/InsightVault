import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

# Create your models here.

class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=100.00, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = str(uuid.uuid4().int)[:12]
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

class DebitTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="debit_transactions")
    destination_account_number = models.CharField(max_length=20, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("fraud_blocked", "Fraud Blocked"),
    ]
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="completed")

    def __str__(self):
        return f"{self.account} - {self.amount} ({self.status})"

