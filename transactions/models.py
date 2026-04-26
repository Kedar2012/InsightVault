import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

# Create your models here.


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = str(uuid.uuid4().int)[:12]
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(
        max_length=10,
        choices=[("credit", "Credit"), ("debit", "Debit")]
    )
    description = models.TextField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.transaction_type == "debit" and self.account.balance < self.amount:
            raise ValidationError("Insufficient balance for this transaction.")
        
        super().save(*args, **kwargs)
        if self.transaction_type == "credit":
            self.account.balance += self.amount
        elif self.transaction_type == "debit":
            self.account.balance -= self.amount
        self.account.save()
    
    def __str__(self):
        return f"{self.transaction_type} {self.amount} on {self.account.account_number}"