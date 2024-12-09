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

