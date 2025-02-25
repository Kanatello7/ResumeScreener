from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.parsers import MultiPartParser
from .models import Job, Resume
from .forms import JobPostForm, ResumeUploadForm
import os 
from django.conf import settings
from .views import extract_archive
from django.core.exceptions import ValidationError
from django.core.files import File  

from rest_framework.parsers import JSONParser

class JobSerializer(serializers.ModelSerializer):
    resume_count = serializers.SerializerMethodField()
    posted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Job
        fields = [
            'id', 'job_title', 'location', 'experience_level',
            'employment_type', 'requirements', 'skills', 'posted_at',
            'resume_count'
        ]

    def get_resume_count(self, obj):
        return obj.resumes.count()
class DashboardResponseSchema:
    JOB_LIST = openapi.Response(
        description='List of recent jobs with resume counts',
        schema=JobSerializer(many=True)
)
    
class DashboardAPI(APIView):
    @swagger_auto_schema(
        operation_description="Get dashboard data with recent job postings",
        responses={
            200: DashboardResponseSchema.JOB_LIST,
            401: "Unauthorized"
        },
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Bearer token',
                required=True
            )
        ]
    )
    def get(self, request):
        recent_jobs = Job.objects.filter(employer=request.user).order_by('-posted_at')[:10]
        serializer = JobSerializer(recent_jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class JobPostAPI(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Post a new job",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['job_title', 'location', 'experience_level', 'employment_type'],
            properties={
                'job_title': openapi.Schema(type=openapi.TYPE_STRING),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'experience_level': openapi.Schema(type=openapi.TYPE_STRING, enum=['entry', 'mid', 'senior']),
                'employment_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['full-time', 'part-time', 'contract']),
                'requirements': openapi.Schema(type=openapi.TYPE_STRING),
                'skills': openapi.Schema(type=openapi.TYPE_STRING),
                'responsibilities': openapi.Schema(type=openapi.TYPE_STRING),
                'job_description': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            302: openapi.Response(
                description="Redirect to upload resumes page",
                headers={
                    'Location': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example='/upload-resumes/1/'
                    )
                }
            ),
            400: openapi.Response('Validation error', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ))
        }
    )
    def post(self, request):
        data = request.data
        form = JobPostForm(data)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user
            job.save()
            return Response(
                status=status.HTTP_302_FOUND,
                headers={'Location': f'/upload-resumes/{job.id}/'}
            )
        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

class UploadResumesAPI(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Upload resumes for a job",
        manual_parameters=[
            openapi.Parameter(
                'job_id',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description='ID of the job to upload resumes for'
            ),
            openapi.Parameter(
                'resume_files',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='Resume files to upload (PDF, DOCX, RAR, ZIP)',
                required=True
            )
        ],
        responses={
            302: openapi.Response(
                description="Redirect to job posts page",
                headers={
                    'Location': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example='/candidates/job_posts/1/'
                    )
                }
            ),
            400: openapi.Response('Validation error', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ))
        }
    )
    def post(self, request, job_id):
        job = Job.objects.get(id=job_id)
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_files = []
            for uploaded_file in request.FILES.getlist('resume_files'):
                if uploaded_file.name.endswith('.rar') or uploaded_file.name.endswith('.zip'):
                    try:
                        extract_dir = os.path.join(settings.MEDIA_ROOT, 'temp_extracted_files')
                        os.makedirs(extract_dir, exist_ok=True)
                        extract_archive(uploaded_file, extract_dir)
                        for root, _, files in os.walk(extract_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                with open(file_path, 'rb') as f:
                                    django_file = File(f, name=file)
                                    Resume.objects.create(job=job, resume_file=django_file)
                                    uploaded_files.append(file)
                        for root, _, files in os.walk(extract_dir):
                            for file in files:
                                os.remove(os.path.join(root, file))
                        os.rmdir(extract_dir)
                    except ValidationError as e:
                        continue
                else:
                    Resume.objects.create(job=job, resume_file=uploaded_file)
                    uploaded_files.append(uploaded_file.name)
            return Response(
                status=status.HTTP_302_FOUND,
                headers={'Location': f'/candidates/job_posts/{job.id}/'}
            )
        return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

class AuthResponseSchemas:
    HTML_FORM = openapi.Response(
        description='HTML Form Response',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'form': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='HTML form content'
                )
            }
        )
    )
    
    REDIRECT_RESPONSE = openapi.Response(
        description='Redirect Response',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'redirect': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Redirect URL'
                )
            }
        )
    )
    
    ERROR_RESPONSE = openapi.Response(
        description='Error Response',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'errors': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Validation errors'
                )
            }
        )
    )

class LoginAPI(APIView):
    @swagger_auto_schema(
        operation_description="Display login form",
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request):
        return Response({"detail": "Login form"})
    
    @swagger_auto_schema(
        operation_description="Authenticate user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            302: AuthResponseSchemas.REDIRECT_RESPONSE,
            400: AuthResponseSchemas.ERROR_RESPONSE
        }
    )
    def post(self, request):
        return Response({"redirect": "/dashboard/"})

class LogoutAPI(APIView):
    @swagger_auto_schema(
        operation_description="Log out user",
        responses={
            302: AuthResponseSchemas.REDIRECT_RESPONSE
        }
    )
    def get(self, request):
        return Response({"redirect": "/login/"})

class PasswordChangeAPI(APIView):
    @swagger_auto_schema(
        operation_description="Display password change form",
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request):
        return Response({"detail": "Password change form"})
    
    @swagger_auto_schema(
        operation_description="Submit password change",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['old_password', 'new_password1', 'new_password2'],
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password1': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password2': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            302: AuthResponseSchemas.REDIRECT_RESPONSE,
            400: AuthResponseSchemas.ERROR_RESPONSE
        }
    )
    def post(self, request):
        return Response({"redirect": "/password_change/done/"})

class PasswordChangeDoneAPI(APIView):
    @swagger_auto_schema(
        operation_description="Password change success page",
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request):
        return Response({"detail": "Password changed successfully"})

class PasswordResetAPI(APIView):
    @swagger_auto_schema(
        operation_description="Display password reset form",
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request):
        return Response({"detail": "Password reset form"})
    
    @swagger_auto_schema(
        operation_description="Request password reset",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
            }
        ),
        responses={
            302: AuthResponseSchemas.REDIRECT_RESPONSE,
            400: AuthResponseSchemas.ERROR_RESPONSE
        }
    )
    def post(self, request):
        return Response({"redirect": "/password_reset/done/"})

class PasswordResetDoneAPI(APIView):
    @swagger_auto_schema(
        operation_description="Password reset email sent confirmation",
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request):
        return Response({"detail": "Password reset email sent"})

class PasswordResetConfirmAPI(APIView):
    @swagger_auto_schema(
        operation_description="Display password reset confirmation form",
        manual_parameters=[
            openapi.Parameter(
                'uidb64',
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Base64 encoded user ID'
            ),
            openapi.Parameter(
                'token',
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Password reset token'
            )
        ],
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request, uidb64, token):
        return Response({"detail": "Password reset confirmation form"})
    
    @swagger_auto_schema(
        operation_description="Submit new password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_password1', 'new_password2'],
            properties={
                'new_password1': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password2': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            302: AuthResponseSchemas.REDIRECT_RESPONSE,
            400: AuthResponseSchemas.ERROR_RESPONSE
        }
    )
    def post(self, request, uidb64, token):
        return Response({"redirect": "/reset/done/"})

class PasswordResetCompleteAPI(APIView):
    @swagger_auto_schema(
        operation_description="Password reset completion page",
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request):
        return Response({"detail": "Password reset complete"})

class SignupAPI(APIView):
    @swagger_auto_schema(
        operation_description="Display registration form",
        responses={200: AuthResponseSchemas.HTML_FORM}
    )
    def get(self, request):
        return Response({"detail": "Registration form"})
    
    @swagger_auto_schema(
        operation_description="Register new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password1', 'password2'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password1': openapi.Schema(type=openapi.TYPE_STRING),
                'password2': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            302: AuthResponseSchemas.REDIRECT_RESPONSE,
            400: AuthResponseSchemas.ERROR_RESPONSE
        }
    )
    def post(self, request):
        return Response({"redirect": "/register/done/"})