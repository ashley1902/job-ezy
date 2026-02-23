from http.client import HTTPResponse
from django.shortcuts import render

####
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .userProfileSerializer import userProfileSerializer
from .models import Profile



# Create your views here.


def user_profile_health(request):
    return HTTPResponse("<h1>Hello! This is the accounts page.")


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated] # Must be logged in via JWT

    # 1. GET: Retrieve user's own profile
    def get(self, request):
        try:
            profile = request.user.profile
            serializer = userProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

    # 2. POST: Create profile
    def post(self, request):
        # Check if profile already exists
        if Profile.objects.filter(user=request.user).exists():
            return Response({"error": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = userProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Attach the logged-in user to the profile
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 3. PUT: Update profile
    def put(self, request):
        try:
            profile = request.user.profile
            # 'partial=True' allows updating just one field (like only skills)
            serializer = userProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"error": "Profile does not exist"}, status=status.HTTP_404_NOT_FOUND)
        

