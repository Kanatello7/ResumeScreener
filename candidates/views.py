from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import Job, Resume

@login_required
def job_posts(request, job_id):
    job = Job.objects.get(id=job_id)
    resumes = job.resumes.all()
    return render(request,'candidates/job-posts.html',{'job': job,
                                                       'resumes': resumes})
    
@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.job.employer != request.user:
        return redirect('dashboard')  

    resume.delete()
    return redirect('candidates:job_posts', job_id=resume.job.id)