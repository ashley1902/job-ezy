from django.shortcuts import render

from django.http import HttpResponse
import requests
from accounts.models import User
from user_profile.models import Profile
from user_profile.userProfileSerializer import userProfileSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.


def user_profile_manager_health(request):
    return HttpResponse("<h1>Hello! This is the accounts page.")

class AdminProfileManagerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def check_admin(self, request, fields=None):
        # return getattr(user, 'role', '') == 'admin'
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
        """Admin can fetch all profiles or a specific one"""
        # if not self.check_admin(request.data.get("role")):
            # return Response({"error": "Admin access required"}, status=403)

        auth_data = self.check_admin(request, fields=["role", "firstName", "lastName"])
        authorized_roles = ["admin"]
        if not auth_data or auth_data.get("role") not in authorized_roles:
            return Response({"error": "Admin access required"}, status=403)

        target_username = request.data.get('username')
        
        if target_username:
            try:
                user = User.objects.get(username=target_username)
                serializer = userProfileSerializer(user.profile)
                return Response(serializer.data)
            except (User.DoesNotExist, Profile.DoesNotExist):
                return Response({"error": "User/Profile not found"}, status=404)
        
        # Fetch all profiles
        profiles = Profile.objects.all()
        serializer = userProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def put(self, request):
        """Admin can modify any user's profile"""
        auth_data = self.check_admin(request, fields=["role", "firstName", "lastName"])
        authorized_roles = ["admin"]
        if not auth_data or auth_data.get("role") not in authorized_roles:
            return Response({"error": "Admin access required"}, status=403)

        target_username = request.data.get('username')
        print("target_username: ", target_username)
        # try:
        #     user = User.objects.get(username=target_username)
        #     profile = user.profile
            
        #     # partial=True allows admin to change only specific fields
        #     serializer = userProfileSerializer(profile, data=request.data, partial=True)
        #     if serializer.is_valid():
        #         serializer.save(user=target_username)
        #         return Response(serializer.data)
        #     return Response(serializer.errors, status=400)
        # except User.DoesNotExist:
        #     return Response({"error": "User not found"}, status=404)

        try:
            # 2. Convert the string 'test' into a real User Instance
            target_user_instance = User.objects.get(username=target_username)
            target_profile_instance = target_user_instance.profile

            # 3. Initialize serializer with the profile instance
            # IMPORTANT: We do NOT pass 'user' in the data dictionary 
            # because your serializer has 'username' as ReadOnly.
            serializer = userProfileSerializer(
                target_profile_instance, 
                data=request.data, 
                partial=True
            )

            if serializer.is_valid():
                # 4. Save without passing any extra user arguments
                serializer.save() 
                return Response(serializer.data)
        
            return Response(serializer.errors, status=400)
        except User.DoesNotExist:
            return Response({"error": f"User {target_username} not found"}, status=404)



    def delete(self, request):
        """Admin can delete a user (and their profile)"""
        auth_data = self.check_admin(request, fields=["role", "firstName", "lastName", "username"])
        authorized_roles = ["admin"]
        if not auth_data or auth_data.get("role") not in authorized_roles:
            return Response({"error": "Admin access required"}, status=403)

        target_username = request.data.get('username')
        try:
            user = User.objects.get(username=target_username)
            if target_username == auth_data.get("username"):
                return Response({"error": "Admin cannot delete themselves"}, status=400)
            
            user.delete() # Deletes user and associated profile via cascade
            return Response({"message": f"User {target_username} deleted successfully"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        

