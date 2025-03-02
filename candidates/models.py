from django.db import models
from account.models import Job, Resume

class Candidate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='candidate')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    sections = models.JSONField(default=dict, blank=True, null=True)
    details = models.JSONField(default=dict, blank=True, null=True)   
    parsed_text = models.TextField()
    match_percentage = models.FloatField(default=0.0)
    ai_comment = models.TextField(blank=True, null=True)
    interview_questions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.role})"