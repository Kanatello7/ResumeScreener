from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import Job, Resume
from .models import Candidate
from django.shortcuts import redirect
from urllib.parse import quote
from .resumeparser import ResumeParser
from sentence_transformers import SentenceTransformer
import math
from dotenv import load_dotenv
import os
import json
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key = os.getenv('OPEN_AI_KEY',)
)

def create_job_text(job_data):
    text_parts = []
    text_parts.append(f"Job Title: {job_data.job_title}")
    text_parts.append(f"Location: {job_data.location}")
    text_parts.append(f"Experience Level: {job_data.experience_level}")
    text_parts.append(f"Employment Type: {job_data.employment_type}")
    text_parts.append(f"Description: {job_data.job_description}")
    text_parts.append(f"Requirements: {job_data.requirements}")
    text_parts.append(f"Skills: {job_data.skills}")
    text_parts.append(f"Responsibilities: {job_data.responsibilities}")

    return "\n".join(text_parts)

def check_detail(detail, default):
    if detail == "Not found":
        return default 
    return detail

def create_candidate_text(candidate_data):

    text_parts = []
    text_parts.append(f"Full Name: {candidate_data.get('full_name', '')}")
    text_parts.append(f"Job Title: {candidate_data.get('job_title', '')}")
    text_parts.append(f"Location: {candidate_data.get('location', '')}")
    text_parts.append(f"Statement: {candidate_data.get('statement', '')}")
    text_parts.append(f"Total Experience (Years): {candidate_data.get('total_experience_year', '')}")

    # Skills:
    skills = check_detail(candidate_data.get("skills", []), [])

    text_parts.append("Skills: " + ", ".join(skills))

    # Experience:
    experiences = check_detail(candidate_data.get("experience", []), [])
    for exp in experiences:
        text_parts.append(
            f"Experience at {exp.get('Company Name', '')} as {exp.get('job_title', '')}: {exp.get('responsibilities', [])}")

    # Projects:
    projects = check_detail(candidate_data.get("projects", []), [])
    for proj in projects:
        text_parts.append(
            f"Project: {proj.get('title', '')}. Tech used: {proj.get('tech_used', [])}. {proj.get('description', '')}")

    # Awards:
    awards = check_detail(candidate_data.get("awards", []), [])
    for award in awards:
        text_parts.append(f"Award: {award.get('title', '')}. {award.get('description', '')}")

    # Languages
    languages = check_detail(candidate_data.get('languages', []), [])
    text_parts.append("Languages: " + ", ".join(languages))
    
    return "\n".join(text_parts)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def get_embedding(text):
    embedding = model.encode(text)
    return embedding

def cosine_similarity(a, b):
    dot = 0.0
    a_norm = 0.0
    b_norm = 0.0

    for x, y in zip(a, b):
        dot += x*y
        a_norm += x*x
        b_norm += y*y

    if a_norm == 0.0 or b_norm == 0.0:
        return 0.0
    return dot / (math.sqrt(a_norm) * math.sqrt(b_norm))

def parse_resume(resume_id, file_path):
    parser = ResumeParser(file_path)
    data = parser.get_extracted_data()
    return resume_id, data

def compute_fit_score(job_data, candidate_data):
    #Text
    job_text = create_job_text(job_data)
    candidate_text = create_candidate_text(candidate_data)

    #Embeddings
    job_emb = get_embedding(job_text)
    candidate_emb = get_embedding(candidate_text)

    #Cosine similarity
    similarity = cosine_similarity(job_emb, candidate_emb)

    fit_score = (similarity + 1) / 2 * 100
    return round(fit_score, 2)

def gpt_match_score(job, candidate_data):
    system_prompt = "You are an expert career coach. You assess how well a candidate fits a job."
    
    fields = ['job_title','location','experience_level','employment_type','requirements', 'skills', 'responsibilities', 'job_description']
    job_data = {field: getattr(job, field, "") for field in fields}
    print(job_data)
    user_prompt = f"""
    Job Details:
    {json.dumps(job_data, indent=2)}

    Candidate Details:
    {json.dumps(candidate_data, indent=2)}

    Please provide a single numeric score from 0 to 100 to indicate the candidate's overall match for the job.
    Also provide a short explanation after the score, like this format:

    {{
      "match_score": 87,
      "explanation": "Short sentence explaining reasoning."
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    cleaned_json = response.choices[0].message.content.strip("```json").strip("```").strip()
    res = json.loads(cleaned_json)
    return res

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
            gpt_res = gpt_match_score(job, data.get('details'))
            Candidate.objects.create(
                job=job,
                resume=resume_obj,       
                name=data.get('full_name'),
                email=data.get('email','Unknown'),
                sections=data.get('sections'),
                details=data.get('details'),
                parsed_text=data.get('raw_text'),
                #match_percentage=compute_fit_score(job, data.get('details'))
                match_percentage=gpt_res['match_score'],
                ai_comment=gpt_res['explanation']
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