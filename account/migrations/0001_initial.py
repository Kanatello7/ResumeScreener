# Generated by Django 5.1.6 on 2025-02-18 17:10

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=100)),
                ('experience_level', models.CharField(choices=[('entry', 'Entry (0-1 years)'), ('mid', 'Mid (1-3 years)'), ('senior', 'Senior (3+ years)')], max_length=20)),
                ('employment_type', models.CharField(choices=[('full-time', 'Full-Time'), ('part-time', 'Part-Time'), ('online', 'Online')], max_length=20)),
                ('requirements', models.TextField()),
                ('skills', models.TextField()),
                ('responsibilities', models.TextField()),
                ('job_description', models.TextField()),
                ('posted_at', models.DateTimeField(auto_now_add=True)),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resume_file', models.FileField(upload_to='resumes/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'rar', 'zip'])])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to='account.job')),
            ],
        ),
    ]
