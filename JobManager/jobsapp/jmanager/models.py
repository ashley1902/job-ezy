from django.db import models

class Job(models.Model):
    jobid = models.IntegerField(unique=True)
    # Added jobName field as requested
    jobName = models.CharField(max_length=50) 
    jobLocation = models.CharField(max_length=60)
    jobCountry = models.CharField(max_length=60)
    createDate = models.DateTimeField(auto_now_add=True)
    updateDate = models.DateTimeField(auto_now=True)
    department = models.CharField(max_length=30)
    jobDescription = models.CharField(max_length=500)
    requirement = models.CharField(max_length=300)
    yearsOfExp = models.DecimalField(max_digits=3, decimal_places=1)
    aboutDesc = models.CharField(max_length=300)
    creatorName = models.CharField(max_length=50)
    updatorName = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    tags = models.JSONField(default=list)

    def __str__(self):
        return f"{self.jobid} - {self.jobName}"