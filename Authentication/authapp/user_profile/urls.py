"""
authapp/user_profile/urls.py
"""
from django.urls import path

####
from . import views

urlpatterns = [
    path("profile/health/", views.user_profile_health, name="accounts"),
    path("profile", views.UserProfileAPIView.as_view(), name="profile")
]
