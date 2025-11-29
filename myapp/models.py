from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Add additional fields as needed for your application.
    """
    # Example: Add custom fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
