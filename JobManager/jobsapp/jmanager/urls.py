from django.urls import path
from . import views

urlpatterns = [
    path('health', views.jmanagerHealth, name='job_Manager Health'),
    path('manage', views.jManagerAPIView.as_view(), name='job_Manager')
    # path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
]