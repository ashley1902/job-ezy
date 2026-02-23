from django.shortcuts import render
from django.http import HttpResponse
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Job
from .jobSerializer import jobSerializer


# Create your views here.

def jmanagerHealth(request):
    return HttpResponse("Hi!! This is job Manager")


class jManagerAPIView(APIView):
    # Public access for GET, but logic inside validates tokens for other methods
    permission_classes = [AllowAny]

    def get_auth_data(self, request, fields=None):
        """Internal helper to communicate with the Auth App."""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
            
        payload = {"fields": fields if fields else []}
        try:
            # Change this URL if your Auth App is hosted elsewhere
            response = requests.post(
                "http://127.0.0.1:8000/int/accounts/validate", 
                json=payload,
                headers={"Authorization": auth_header}
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def get(self, request):
        """
        Handles two modes:
        1. ?all=true -> Returns list of active jobs with summary fields.
        2. ?all=false&jobid=X -> Returns full details for a specific job.
        """
        show_all_jobs = request.query_params.get('all', 'false').lower() == 'true'
        inactive_filter = request.query_params.get('inactive', 'false').lower() == 'true'
        requested_fields = request.data.get('fields')

        if show_all_jobs:
            jobs = Job.objects.filter(is_active=True) if not inactive_filter else Job.objects.all()
            
            summary_fields = ['jobid', 'jobName', 'jobLocation', 'createDate', 'updateDate', 'department']
            
            if requested_fields and isinstance(requested_fields, list):
                # print("Requested additional fields:", request.data.get('fields'))
                summary_fields.extend(requested_fields)
                summary_fields = list(set(summary_fields)) # Add requested summary fields to default summary fields, using set and then list to remove duplicates
            else:
                summary_fields          
                       
            serializer = jobSerializer(jobs, many=True)
            filtered_data = [
                {field: job[field] for field in summary_fields if field in job}
                for job in serializer.data
            ]
            return Response(filtered_data, status=status.HTTP_200_OK)

        else:
            target_jobid = request.query_params.get('jobid')
            if not target_jobid:
                return Response({"error": "jobid is required when all=false"}, status=400)
            
            try:
                # Only fetch if active
                job = Job.objects.get(jobid=target_jobid, is_active=True) if not inactive_filter else Job.objects.get(jobid=target_jobid)
                serializer = jobSerializer(job)
                if requested_fields and isinstance(requested_fields, list):
                    # print("Requested fields for single job:", request.data.get('fields'))
                    filtered_data = {field: serializer.data[field] for field in requested_fields if field in serializer.data}
                    return Response(filtered_data, status=status.HTTP_200_OK)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Job.DoesNotExist:
                return Response({"error": "Active job not found"}, status=404)

    def post(self, request):
        """Create a new job. Requires 'recruiter' role."""
        auth_data = self.get_auth_data(request, fields=["role", "firstName", "lastName"])
        authorized_roles = ["recruiter", "admin"]
        if not auth_data or auth_data.get("role") not in authorized_roles:
            return Response({"error": "Only Recruiter/Admin is authorized to create a job"}, status=403)

        serializer = jobSerializer(data=request.data)
        if serializer.is_valid():
            full_name = f"{auth_data['firstName']} {auth_data['lastName']}"
            serializer.save(creatorName=full_name, updatorName=full_name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update an existing job. Requires 'recruiter' role."""
        auth_data = self.get_auth_data(request, fields=["role", "firstName", "lastName"])
        authorized_roles = ["recruiter", "admin"]
        if not auth_data or auth_data.get("role") not in authorized_roles:
            return Response({"error": "Only Recruiter/Admin is authorized to update a job"}, status=403)

        job_id = request.data.get("jobid")
        try:
            job = Job.objects.get(jobid=job_id, is_active=True)
        except Job.DoesNotExist:
            return Response({"error": "Active job not found"}, status=404)

        serializer = jobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            full_name = f"{auth_data['firstName']} {auth_data['lastName']}"
            serializer.save(updatorName=full_name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Soft-delete a job by setting is_active to False."""
        auth_data = self.get_auth_data(request, fields=["role", "firstName", "lastName"])
        authorized_roles = ["recruiter", "admin"]
        if not auth_data or auth_data.get("role") not in authorized_roles:
            return Response({"error": "Only Recruiter/Admin is authorized to delete a job"}, status=403)

        job_id = request.data.get("jobid")
        try:
            job = Job.objects.get(jobid=job_id, is_active=True)
            job.is_active = False
            job.updatorName = f"{auth_data['firstName']} {auth_data['lastName']}"
            job.updateDate = job.updateDate  # Trigger auto_now update
            job.save()
            return Response({"message": f"Job {job_id} deactivated"}, status=200)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)
        
    
    def patch(self, request):
        """Soft-restore a job by setting is_active to True."""
        auth_data = self.get_auth_data(request, fields=["role", "firstName", "lastName"])
        authorized_roles = ["admin"]
        if not auth_data or auth_data.get("role") not in authorized_roles:
            return Response({"error": "Only Admin is authorized to restore a job"}, status=403)

        job_id = request.data.get("jobid")
        try:
            job = Job.objects.get(jobid=job_id, is_active=False)
            job.is_active = True
            job.updatorName = f"{auth_data['firstName']} {auth_data['lastName']}"
            job.updateDate = job.updateDate  # Trigger auto_now update
            job.save()
            return Response({"message": f"Job {job_id} reactivated", "jobid": job_id}, status=200)
        except Job.DoesNotExist:
            return Response({"error": "Job either not found or is already active"}, status=404)