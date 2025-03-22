from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import Job, Resume
from .models import Candidate
from django.shortcuts import redirect
from urllib.parse import quote
from .resumeparser import ResumeParser
import json

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
                details=data.get('details'),
                parsed_text=data.get('raw_text'),
            )
    candidates = job.candidates.all()
    
    name_query = request.GET.get('name', '')
    min_match = request.GET.get('min_match', 0)

    if name_query:
        candidates = candidates.filter(name__icontains=name_query)
    
    if min_match:
        candidates = candidates.filter(match_percentage__gte=float(min_match))
        
    return render(request, 'candidates/job-posts.html', {
        'job': job,
        'candidates': candidates,
        'current_filters': {
            'name': name_query,
            'min_match': min_match
        }
    })



def view_resume(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    resume_url = request.build_absolute_uri(candidate.resume.resume_file.url)
    google_docs_url = f"https://docs.google.com/viewer?url={quote(resume_url)}"
    return redirect(google_docs_url)

def handle_value(value, new_entity):
    if type(value) == list:
        if new_entity:
            return "<br><br>".join(handle_value(v, True) for v in value)
        else:
            return "<br>"+ "<br>".join("● "+ handle_value(v, False) for v in value)
    elif type(value) == dict:
        res = ""
        for k, v in value.items():
            v = handle_value(v, new_entity=False)
            if v == 'Not found' or v == "<br>":
                continue
            res += f"<strong>{k.replace('_', ' ').capitalize()}</strong>: {v}<br>"
        return res
    else:
        return value
    
def prettify_details(details):
    res = {"Personal Information": ""}
    personal_info = ""
    for key, value in details.items():

        if key in ['full_name','job title', 'email','phone','location']:
            personal_info += f"<strong>{key.capitalize().replace('_', ' ')}</strong>: {value}" + "<br>"
        elif key in ['skills', 'languages']:
            if value == 'Not found':
                continue
            res[key] = ", ".join(value)
            
        else:
            v = handle_value(value, new_entity=True)
            if v == 'Not found':
                continue
            res[key] = v

    res['Personal Information'] = personal_info
    return res 

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
    
    details = prettify_details(candidate.details)
    
    return render(request, 'candidates/profile.html', {'candidate':candidate,
                                                       'job':job,
                                                       'ext':ext,
                                                       'existed_sections': details})

@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)
    if resume.job.employer != request.user:
        return redirect('dashboard')  

    resume.delete()
    return redirect('candidates:job_posts', job_id=resume.job.id)