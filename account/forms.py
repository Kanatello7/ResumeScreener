from django import forms 
from django.contrib.auth.models import User
from .models import Job, Resume

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email']
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
    
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data

class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'job_title', 'location', 'experience_level', 
            'employment_type', 'requirements', 'skills', 
            'responsibilities', 'job_description'
        ]
        widgets = {
            'job_title': forms.TextInput(attrs={
                'placeholder': 'e.g. Frontend Developer',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g. New York, NY (Remote Available)',
                'class': 'form-control'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'requirements': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter the key requirements...',
                'class': 'form-control'
            }),
            'skills': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter required skills...',
                'class': 'form-control'
            }),
            'responsibilities': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter key responsibilities...',
                'class': 'form-control'
            }),
            'job_description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter the full job description...',
                'class': 'form-control'
            }),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    template_name = 'widgets/multiple_file_input.html'  # Create this template

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'class': 'custom-file-input'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]

class ResumeUploadForm(forms.ModelForm):
    resume_files = MultipleFileField(label='', required=True)

    class Meta:
        model = Resume
        fields = []
    
    def clean(self):
        cleaned_data = super().clean()
        files = self.files.getlist('resume_files')
        if len(files) == 0:
            self.add_error('resume_files', 'Please upload at least one file.')
        else:
            for file in files:
                ext = file.name.split('.')[1]
                if ext not in ['pdf', 'docx', 'rar', 'zip']:
                    self.add_error('resume_files', f'File extension "{ext}" is not allowed. Allowed extensions are: pdf, docx, rar, zip.')
        return cleaned_data