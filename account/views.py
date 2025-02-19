# jobs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import JobPostForm, ResumeUploadForm, UserRegistrationForm
from .models import Job, Resume
from django.conf import settings
import os
import tempfile
import patoolib
from django.core.exceptions import ValidationError
from django.core.files import File  

@login_required
def dashboard(request):
    recent_jobs = Job.objects.filter(employer=request.user).order_by('-posted_at')[:10]
    jobs = []
    for job in recent_jobs:
        jobs.append((job,job.resumes.all()))
    print(jobs)
    return render(request,'account/dashboard.html',{'recent_jobs': jobs})
    
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password'])
            new_user.save()
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            return redirect('upload_resumes', job_id=job.id)
    else:
        form = JobPostForm()
    return render(request, 'account/post_job.html', {'form': form})

def extract_archive(uploaded_file, extract_dir):
    """
    Extract an archive file to the specified directory.
    """
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        # Extract the archive
        patoolib.extract_archive(tmp_file_path, outdir=extract_dir)

        # Clean up the temporary file
        os.remove(tmp_file_path)
    except patoolib.util.PatoolError as e:
        raise ValidationError(f"Unable to extract archive: {e}")
    except Exception as e:
        raise ValidationError(f"An error occurred: {e}")

@login_required
def upload_resumes(request, job_id):
    job = Job.objects.get(id=job_id)
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            for uploaded_file in request.FILES.getlist('resume_files'):
                if uploaded_file.name.endswith('.rar') or uploaded_file.name.endswith('.zip'):
                    try:
                        # Create a temporary directory for extraction
                        extract_dir = os.path.join(settings.MEDIA_ROOT, 'temp_extracted_files')
                        os.makedirs(extract_dir, exist_ok=True)

                        # Extract the archive
                        extract_archive(uploaded_file, extract_dir)

                        # Process extracted files
                        for root, _, files in os.walk(extract_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                with open(file_path, 'rb') as f:
                                    # Wrap the file object in Django's File class
                                    django_file = File(f, name=file)
                                    Resume.objects.create(job=job, resume_file=django_file)

                        # Clean up the temporary directory
                        for root, _, files in os.walk(extract_dir):
                            for file in files:
                                os.remove(os.path.join(root, file))
                        os.rmdir(extract_dir)
                    except ValidationError as e:
                        print(e)
                        continue
                else:
                    # Handle non-archive files (e.g., .pdf, .docx)
                    Resume.objects.create(job=job, resume_file=uploaded_file)
            return redirect('dashboard')
    else:
        form = ResumeUploadForm()
    return render(request, 'account/upload_resumes.html', {'form': form, 'job': job})

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.employer != request.user:
        return redirect('dashboard')
    job.delete()
    return redirect('dashboard')

@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    # Ensure the user is the owner of the job (optional but recommended)
    if resume.job.employer != request.user:
        return redirect('dashboard')  # Redirect if the user is not the owner
    resume.delete()
    return redirect('dashboard')