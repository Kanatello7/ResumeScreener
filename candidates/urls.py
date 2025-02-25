from django.urls import path, include
from . import views

app_name = 'candidates'

urlpatterns = [
    path('job-posts/<int:job_id>/', views.job_posts, name='job_posts'),
    path('delete-resume/<int:resume_id>', views.delete_resume, name='delete_resume'),
]