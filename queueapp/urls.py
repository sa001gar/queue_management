from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LineViewSet, RegistrationViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'lines', LineViewSet)
router.register(r'registrations', RegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
]



from django.conf import settings # new
from  django.conf.urls.static import static #new


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)