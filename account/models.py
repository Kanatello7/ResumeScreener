from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Job(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
        ('online', 'Online'),
    ]
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry (0-1 years)'),
        ('mid', 'Mid (1-3 years)'),
        ('senior', 'Senior (3+ years)'),
    ]
    
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    requirements = models.TextField()
    skills = models.TextField() 
    responsibilities = models.TextField()
    job_description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.job_title

class Resume(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resumes')
    resume_file = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'rar', 'zip'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume for {self.job.job_title}"
    
@receiver(post_delete, sender=Resume)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Resume` object is deleted.
    """
    if instance.resume_file:
        instance.resume_file.delete(False)