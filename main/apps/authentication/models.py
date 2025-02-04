from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # username, first_name, last_name, password inherited from AbstractUser
    email = models.EmailField(unique=True) # overriding for unique variables
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username