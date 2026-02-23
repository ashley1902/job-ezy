"""
home/urls.py
"""
from django.urls import path, include


####
from . import views


urlpatterns = [
    path('/health', views.home, name='home'),
]
