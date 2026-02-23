"""
authapp/user_profile/userProfileSerializer.py
"""

from rest_framework import serializers
from .models import Profile

class userProfileSerializer(serializers.ModelSerializer):
    # skills is automatically handled as a list by JSONField + ModelSerializer
    skills = serializers.ListField(
        child=serializers.CharField(max_length=100), 
        allow_empty=True
    )
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    role = serializers.ReadOnlyField(source='user.role')

    class Meta:
        model = Profile
        # We exclude 'user' because we will inject it from the request in the view
        fields = [ 
            'username', 'email', 'role', 'firstName', 'lastName', 'DOB', 'email', 
            'phoneNumber', 'highestDegree', 'yearsOfExperience', 'skills'
        ]