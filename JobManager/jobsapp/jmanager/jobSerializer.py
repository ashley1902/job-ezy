from rest_framework import serializers
from django.utils import timezone
from django.utils.timesince import timesince
from .models import Job

class jobSerializer(serializers.ModelSerializer):
    # Custom format for output (GET) and multiple allowed formats for input (POST/PUT)
    createDate = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M:%S", 
        read_only=True
    )
    updateDate = serializers.DateTimeField(
        format="%d-%m-%Y %H:%M:%S", 
        read_only=True
    )

    class Meta:
        model = Job
        fields = [
            'jobid', 'jobName', 'jobLocation', 'jobCountry', 'createDate', 'updateDate', 'department', 
            'jobDescription', 'requirement', 'yearsOfExp', 
            'aboutDesc', 'creatorName', 'updatorName', 'is_active'
        ]
        # These fields are managed by the system, not the user
        read_only_fields = ('creatorName', 'updatorName', 'createDate', 'updateDate', 'is_active')

    def validate_jobid(self, value):
        """Ensures jobid does not exceed 4 digits."""
        if value > 9999:
            raise serializers.ValidationError("jobid must be a maximum of 4 digits.")
        return value
    
    def _get_relative_time(self, timestamp):
        """Helper logic to calculate 'Just now' vs 'X time ago'"""
        if not timestamp:
            return None
            
        now = timezone.now()
        diff = now - timestamp

        if diff.total_seconds() < 60:
            return "Just now"
        
        # Get the first part of timesince (e.g., "1 minute" instead of "1 minute, 0 seconds")
        return f"{timesince(timestamp, now).split(',')[0]} ago"

    def get_created_ago(self, obj):
        return self._get_relative_time(obj.createDate)

    def get_last_updated_ago(self, obj):
        return self._get_relative_time(obj.updateDate)