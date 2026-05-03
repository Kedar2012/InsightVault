from django.db import models
from transactions.models import CreditRequest, DebitTransaction
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class FraudFlag(models.Model):
    transaction = models.OneToOneField(
        DebitTransaction,
        on_delete=models.CASCADE,
        related_name="fraud_flag",
        null=True, blank=True
    )
    credit_request = models.ForeignKey(
        CreditRequest, on_delete=models.CASCADE,
        null=True, blank=True
    )
    reason = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="low"
    )
    flagged_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        if self.transaction:
            return f"FraudFlag for Tx {self.transaction.id} ({self.reason})"
        elif self.credit_request:
            return f"FraudFlag for CreditRequest {self.credit_request.id} ({self.reason})"
        return f"FraudFlag ({self.reason})"


# class FraudEventLog(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     event_type = models.CharField(max_length=100)   # e.g. "failed_login", "blocked_account"
#     details = models.JSONField(default=dict, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.event_type} for {self.user if self.user else 'Unknown'}"
    
