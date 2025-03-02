from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Authentication API Documentation",
        default_version='v1',
        description="Complete documentation for all authentication endpoints",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="jetrykanat@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    patterns=[
        path('', include('account.urls')),
    ],
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('candidates/', include('candidates.urls')),
    path('jobs/', include('jobs.urls')),
    # Swagger documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)