from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("analyst", "Analyst"),
        ("support", "Support"),
        ("end_user", "End User"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="end_user")

    def __str__(self):
        return f"{self.username} ({self.role})"
    

