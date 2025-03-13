from django.urls import include, path 
from . import views

app_name = 'reports'

urlpatterns = [
    path('jobs-report', views.jobs_report, name='jobs_report')
]