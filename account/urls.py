from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('post-job/', views.post_job, name='post_job'),
    path('upload-resumes/<int:job_id>/', views.upload_resumes, name='upload_resumes'),
    
    
]