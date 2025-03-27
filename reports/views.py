from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.models import Job
from django.utils import timezone
from account.models import Job, Resume
from candidates.models import Candidate
from datetime import datetime
from collections import defaultdict
from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Count


def get_charts(request, jobs):
    dayly_jobs = (
        Job.objects.filter(employer=request.user)
        .annotate(day=TruncDay('posted_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    
    skills_distribution = defaultdict(int)
    for job in jobs:
        for candidate in job.candidates.all():
            if candidate.details.get('skills'):
                for skill in candidate.details['skills']:
                    skills_distribution[skill.strip()] += 1

    candidate_distribution = {
        job.job_title: job.candidates.count()
        for job in jobs
    }
    
    score_comparison = {
        'job_titles': [],
        'top_scores': [],
        'avg_scores': []
    }
    
    for job in jobs:
        candidates = job.candidates.all()
        if candidates:
            top_score = max(c.match_percentage for c in candidates)
            avg_score = sum(c.match_percentage for c in candidates) / len(candidates)
            
            score_comparison['job_titles'].append(job.job_title[:20] + ('...' if len(job.job_title) > 20 else ''))
            score_comparison['top_scores'].append(top_score)
            score_comparison['avg_scores'].append(avg_score)
    

    chart_data = {
        'days': [entry['day'].strftime('%d %b') for entry in dayly_jobs],
        'jobs_count': [entry['count'] for entry in dayly_jobs],
        'skills_labels': list(skills_distribution.keys())[:10],  
        'skills_data': list(skills_distribution.values())[:10],
        'job_titles': list(candidate_distribution.keys()),
        'candidates_data': list(candidate_distribution.values()),
        'score_comparison': score_comparison
    }
    return chart_data
    
@login_required
def jobs_report(request):
    filter_type = request.GET.get('filter_type', 'all')
    sort_by = request.GET.get('sort_by', 'match')
    date_filter = request.GET.get('date_filter', '')
    
    jobs = Job.objects.filter(employer=request.user)

    if filter_type == 'job_title' and request.GET.get('title') :
        jobs = jobs.filter(job_title=request.GET.get('title'))
    elif filter_type == 'date_posted' and date_filter != '':
        now = timezone.localtime(timezone.now())
        if date_filter == 'today':
            day_ago = now - timezone.timedelta(days=1)
            jobs = [job for job in jobs if job.posted_at >= day_ago]
        elif date_filter == 'week':
            week_ago = now - timezone.timedelta(days=7)
            jobs = [job for job in jobs if job.posted_at >= week_ago]
        elif date_filter == 'month':
            month_ago = now - timezone.timedelta(days=30)
            jobs = [job for job in jobs if job.posted_at >= month_ago]
        
    rows = []
    total_candidates = 0
    total_avg_match = 0 
    
    for job in jobs:
        candidates = job.candidates.all()
        top_candidate_match = -1 
        top_candidate = None 
        avg_match = 0
        skills_freq = {}
        for candidate in candidates:
            if candidate.match_percentage > top_candidate_match: 
                top_candidate_match = candidate.match_percentage
                top_candidate = candidate
            avg_match += candidate.match_percentage
            if candidate.details.get('skills') is not None:
                for skill in candidate.details['skills']:
                    skills_freq[skill] = skills_freq.get(skill, 0) + 1 
        common_skills = ", ".join([key for key, _ in sorted(skills_freq.items(), key=lambda item: item[1], reverse=True)[:3]])
        total_avg_match += avg_match
        if len(candidates):
            avg_match /= len(candidates)
        
        row = {
            'job_title': job.job_title,
            'total_applicants': len(candidates),
            'top_candidate': top_candidate.name if top_candidate else 'N/A',
            'top_score': top_candidate_match,
            'avg_score': avg_match,
            'common_skills': common_skills,
            'posted_at': job.posted_at,
            'date_str': job.posted_at.strftime('%d.%m.%Y')
        }
        rows.append(row)
        total_candidates += len(candidates)
    
    if filter_type == 'min_avg_match':
        if request.GET.get('min_match') and request.GET.get('min_match') != '':
            min_match = int(request.GET.get('min_match'))
        else:
            min_match = 70
        rows = [row for row in rows if row['avg_score'] >= min_match] 
    

    if sort_by == 'date':
        rows = sorted(rows, key=lambda x: x['posted_at'], reverse=True)
    elif sort_by == 'job_title':
        rows = sorted(rows, key=lambda x: x['job_title'])
    else:
        rows = sorted(rows, key=lambda x: x['avg_score'], reverse=True)
    

    if rows:
        total_avg_match = sum(row['avg_score'] for row in rows) / len(rows)
    
    
    chart_data = get_charts(request, jobs)
    return render(request, 'reports/jobs-report.html', {'rows':rows,
                                                        'total_jobs': len(jobs),
                                                        'total_candidates': total_candidates,
                                                        'total_avg_match': total_avg_match,
                                                        'filter_type': filter_type,
                                                        'sort_by': sort_by,
                                                        'date_filter': date_filter,
                                                        'chart_data': chart_data})