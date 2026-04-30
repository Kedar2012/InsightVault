from django.db import models
from transactions.models import Transaction
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class FraudFlag(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="fraud_flag")
    reason = models.TextField()
    flagged_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"FraudFlag for Tx {self.transaction.id}"

# class FraudEventLog(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     event_type = models.CharField(max_length=100)   # e.g. "failed_login", "blocked_account"
#     details = models.JSONField(default=dict, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.event_type} for {self.user if self.user else 'Unknown'}"
    
