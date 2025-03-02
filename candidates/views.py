from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import Job, Resume
from .models import Candidate
from django.shortcuts import redirect
from urllib.parse import quote
from .resumeparser import ResumeParser


def parse_resume(resume_id, file_path):
    parser = ResumeParser(file_path)
    data = parser.get_extracted_data()
    return resume_id, data

@login_required
def job_posts(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    resumes = job.resumes.all()
    
    unparsed_resumes = []
    for resume in resumes:
        if not hasattr(resume, 'candidate'):  
            unparsed_resumes.append((resume.id, resume.resume_file.path))
    
    if unparsed_resumes:
        results = [parse_resume(resume_id, file_path) for (resume_id, file_path) in unparsed_resumes]
        for resume_id, data in results:
            resume_obj = Resume.objects.get(id=resume_id)
            Candidate.objects.create(
                job=job,
                resume=resume_obj,       
                name=data.get('full_name'),
                email=data.get('email','Unknown'),
                sections=data.get('sections'),
                details=data,
                parsed_text=data.get('raw_text'),
            )
    candidates = job.candidates.all()
    
    return render(request, 'candidates/job-posts.html', {
        'job': job,
        'candidates': candidates,
    })



def view_resume(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    resume_url = request.build_absolute_uri(candidate.resume.resume_file.url)
    google_docs_url = f"https://docs.google.com/viewer?url={quote(resume_url)}"
    return redirect(google_docs_url)

@login_required
def candidate_profile(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    if candidate.job.employer != request.user:
        return redirect('dashboard')
    
    if candidate.resume.resume_file.name.endswith('docx'):
        ext = 'docx'
    else:
        ext = 'pdf'
    job = candidate.job
    existed_sections = {'personal information': ""}
    personal_info = ""
    for key, value in candidate.details.items():
        if value != None and value != 'Unknown' and key not in ['raw_text', 'sections'] :
            value = value.replace("\n", "<br>")
            existed_sections[key] = value
        
        if key == 'full_name' or key == 'email' or key == 'phone_number' or key == 'location':
            personal_info += f"{key}: {value}" + "<br>"
    existed_sections['personal information'] = personal_info
    
    return render(request, 'candidates/profile.html', {'candidate':candidate,
                                                       'job':job,
                                                       'ext':ext,
                                                       'existed_sections': existed_sections})

@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.job.employer != request.user:
        return redirect('dashboard')  

    resume.delete()
    return redirect('candidates:job_posts', job_id=resume.job.id)