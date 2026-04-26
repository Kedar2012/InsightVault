import uuid

from django.db import models
from django.conf import settings

# Create your models here.


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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


