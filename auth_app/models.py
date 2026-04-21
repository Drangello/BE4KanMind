from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model for the application.
    
    Extends Django's AbstractUser to use an email as the primary
    authentication identifier instead of a username.

    Attributes:
        email (EmailField): The user's unique email address, used for login.
        fullname (CharField): The user's full name, used for display purposes.
    """
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

