"""
authapp/accounts/urls.py
"""
from django.urls import path

####
from django.urls import include
from . import views

urlpatterns = [
    path("health/", views.acccountshealth, name="accounts"),
    path("login", views.LoginAPIView.as_view(), name="login"),
    path("signup", views.SignupAPIView.as_view(), name="signup"),
    path("logout", views.LogoutAPIView.as_view(), name="logout"),
    path('validate', views.validate_token_dynamic, name='validate-token')
]
