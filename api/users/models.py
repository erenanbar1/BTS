from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user extending Django's AbstractUser.
    Add fields here as needed (phone_number shown as example).
    """
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128)
    

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"