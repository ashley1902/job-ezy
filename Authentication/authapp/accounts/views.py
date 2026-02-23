from http.client import HTTPResponse
from django.shortcuts import render

####
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .loginSerializer import LoginSerializer
from .signupSerializer import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Create your views here.


def acccountshealth(request):
    return HTTPResponse("<h1>Hello! This is the accounts page.")

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "valid": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username
            }, status=status.HTTP_200_OK)

        return Response({"valid": False}, status=status.HTTP_401_UNAUTHORIZED)


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )

        if "username" in serializer.errors:
            return Response(
                {"message": "Existing username"},
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # The frontend must send the refresh token to be blacklisted
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist() 

            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_token_dynamic(request):
    """
    Validates the JWT and returns specific user/profile data.
    Input: {"fields": ["role", "firstName", "lastName"]}
    """
    user = request.user
    # Get the list of fields requested by the calling app (e.g., the Jobs App)
    requested_fields = request.data.get("fields", [])
    
    # Initialize response with the base validity check
    response_data = {
        "is_valid": True
    }

    # Map requested field names to your Custom User and Profile data
    # Profile data is accessed via the 'profile' related_name we set earlier
    field_map = {
        "role": user.role,
        "firstName": getattr(user.profile, 'firstName', None) if hasattr(user, 'profile') else None,
        "lastName": getattr(user.profile, 'lastName', None) if hasattr(user, 'profile') else None,
        "email": user.email,
        "username": user.username
    }

    # Only populate the response with fields that were specifically requested
    for field in requested_fields:
        if field in field_map:
            response_data[field] = field_map[field]

    return Response(response_data)
    
        