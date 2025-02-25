from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from . import docs_views


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('post-job/', views.post_job, name='post_job'),
    path('upload-resumes/<int:job_id>/', views.upload_resumes, name='upload_resumes'),
    
    # Swagger-documented API endpoints
    path('login/', docs_views.LoginAPI.as_view(), name='api-login'),
    path('logout/', docs_views.LogoutAPI.as_view(), name='api-logout'),
    path('password_change/', docs_views.PasswordChangeAPI.as_view(), name='api-password-change'),
    path('password_change/done/', docs_views.PasswordChangeDoneAPI.as_view(), name='api-password-change-done'),
    path('password_reset/', docs_views.PasswordResetAPI.as_view(), name='api-password-reset'),
    path('password_reset/done/', docs_views.PasswordResetDoneAPI.as_view(), name='api-password-reset-done'),
    path('reset/<uidb64>/<token>/', docs_views.PasswordResetConfirmAPI.as_view(), name='api-password-reset-confirm'),
    path('reset/done/', docs_views.PasswordResetCompleteAPI.as_view(), name='api-password-reset-complete'),
    path('register/', docs_views.SignupAPI.as_view(), name='api-register'),
    
    path('post-job/', docs_views.JobPostAPI.as_view(), name='api-post-job'),
    path('upload-resumes/<int:job_id>/', docs_views.UploadResumesAPI.as_view(), name='api-upload-resumes'),
    path('', docs_views.DashboardAPI.as_view(), name='dashboard-api'),
]