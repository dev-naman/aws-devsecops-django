from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class UserMaster(AbstractUser):
    username = models.CharField(max_length=255,unique=True)
    first_name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

class AssetTracker(models.Model):
    user = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    asset_name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=255)
    issue_description = models.TextField()
    ticket_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.asset_name