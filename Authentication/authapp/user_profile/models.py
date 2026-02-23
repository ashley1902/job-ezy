from django.db import models
from django.conf import settings  # Import settings

class Profile(models.Model):
    # Change 'User' to 'settings.AUTH_USER_MODEL'
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    DOB = models.DateField()
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=20)
    highestDegree = models.CharField(max_length=100)
    yearsOfExperience = models.IntegerField()
    skills = models.JSONField(default=list)

    def __str__(self):
        # Access username dynamically
        return f"{self.user.username}'s Profile"