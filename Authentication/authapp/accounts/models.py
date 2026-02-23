from django.db import models

####
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # roles: "user", "recruiter", "admin"
    role = models.CharField(max_length=50, default='user')

    def __str__(self):
        return self.username