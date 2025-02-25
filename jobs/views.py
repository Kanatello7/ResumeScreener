from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import Job
from django.utils import timezone

@login_required
def jobs_list(request):
    jobs_qs = Job.objects.filter(employer=request.user).order_by('-posted_at')
    
    # 1. Filter by candidate count
    candidate_filter = request.GET.get('candidate_filter', '')
    if candidate_filter == '0-10':
        jobs_qs = [job for job in jobs_qs if job.resumes.count() <= 10]
    elif candidate_filter == '10-50':
        jobs_qs = [job for job in jobs_qs if 10 < job.resumes.count() <= 50]
    elif candidate_filter == '50plus':
        jobs_qs = [job for job in jobs_qs if job.resumes.count() > 50]

    # 2. Filter by posted date
    date_filter = request.GET.get('date_filter', '')
    now = timezone.localtime(timezone.now())
    if date_filter == 'today':
        day_ago = now - timezone.timedelta(days=1)
        jobs_qs = [job for job in jobs_qs if job.posted_at >= day_ago]
    elif date_filter == 'week':
        week_ago = now - timezone.timedelta(days=7)
        jobs_qs = [job for job in jobs_qs if job.posted_at >= week_ago]
    elif date_filter == 'month':
        month_ago = now - timezone.timedelta(days=30)
        jobs_qs = [job for job in jobs_qs if job.posted_at >= month_ago]
    jobs = []
    for job in jobs_qs:
        jobs.append((job,len(job.resumes.all())))
    print(jobs)
    return render(request,'jobs/jobs_list.html',{'jobs': jobs})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.employer != request.user:
        return redirect('dashboard')
    job.delete()
    return redirect('jobs:jobs_list')