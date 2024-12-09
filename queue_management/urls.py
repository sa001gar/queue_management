from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Create API info for Swagger documentation
api_info = openapi.Info(
    title="Queue Management API",
    default_version='v1',
    description="API for Queue Management System",
   #  terms_of_service="https://www.yourapp.com/terms/",
   #  contact=openapi.Contact(email="contact@yourapp.com"),
   #  license=openapi.License(name="Your License"),
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='https://trackseries.sagarkundu.live',  # Add your domain
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('queueapp.urls')),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

