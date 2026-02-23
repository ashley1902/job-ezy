"""
authapp/accounts/loginSerializer.py
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(
#             username=data["username"],
#             password=data["password"]
#         )

#         if user is None:
#             raise serializers.ValidationError("Invalid username or password")

#         data["is_valid"] = True
#         return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        # Instead of just "is_valid", we store the actual user object
        data["user"] = user
        return data