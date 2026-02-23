"""
authapp/user_profile_manager_admin/urls.py
"""
from django.urls import path

####
from . import views

urlpatterns = [
    path("health/", views.user_profile_manager_health, name="accounts"),
    path("profileManager", views.AdminProfileManagerAPIView.as_view(), name="profile")
]
