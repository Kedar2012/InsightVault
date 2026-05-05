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
        ("at_support", "At Support"),
    ]
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="completed")
    is_reversed = models.BooleanField(default=False)
    
    @property
    def transaction_type(self):
        return "Debit"

    def __str__(self):
        return f"{self.account} - {self.amount} ({self.status})"

class CreditRequest(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="credit_requests")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_reference = models.CharField(max_length=50)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("fraud_blocked", "Fraud Blocked"),
        ("at_support", "At Support")
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    
    fraud = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account} - {self.amount} ({self.status})"
    
class CreditTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="credit_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_reference = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("fraud_blocked", "Fraud Blocked"),
        ("at_support", "At Support"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    is_reversed = models.BooleanField(default=False)
    
    @property
    def transaction_type(self):
        return "Credit"

    def __str__(self):
        return f"{self.account} - {self.amount} ({self.status})"
    
class ManualDebitTransaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="manul_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="completed")
    is_global = models.BooleanField(default=False)
    is_reversed = models.BooleanField(default=False)

class ReversalTransaction(models.Model):
    debit_transaction = models.ForeignKey(DebitTransaction, on_delete=models.CASCADE, null=True, blank=True)
    credit_transaction = models.ForeignKey(CreditTransaction, on_delete=models.CASCADE, null=True, blank=True)
    manual_debit_transaction = models.ForeignKey(ManualDebitTransaction, on_delete=models.CASCADE, null=True, blank=True)

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="reverse_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="completed")
