from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("analyst", "Analyst"),
        ("support", "Support"),
        ("end_user", "End User"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="end_user")
    blocked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_blocked(self):
        return self.blocked_until and self.blocked_until > timezone.now()
