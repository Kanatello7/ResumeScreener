from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

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