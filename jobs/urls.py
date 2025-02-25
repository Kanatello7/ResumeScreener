from django.urls import path, include
from . import views

app_name = 'jobs'

urlpatterns = [
    path('jobs-list/', views.jobs_list, name='jobs_list'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
]