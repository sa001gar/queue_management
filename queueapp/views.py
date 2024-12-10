from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from .models import Line, Registration
from .serializers import UserSerializer, LineSerializer, RegistrationSerializer
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.exceptions import NotFound, ValidationError
from django.db import transaction

@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['POST'])
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({"success": "Successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You're not logged in."}, status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name='dispatch')
class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pincode']
    search_fields = ['name']

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        try:
            line = self.get_object()
            user = request.user

            with transaction.atomic():
                if Registration.objects.filter(user=user, line=line).exists():
                    return Response({"error": "You are already in this queue."}, status=status.HTTP_400_BAD_REQUEST)

                if line.current_count >= line.capacity:
                    return Response({"error": "This queue is full."}, status=status.HTTP_400_BAD_REQUEST)

                registration = Registration.objects.create(
                    user=user,
                    line=line,
                    name=request.data.get('name', user.get_full_name() or user.username),
                    mobile=request.data.get('mobile'),
                    aadhaar_no=request.data.get('aadhaar_no'),
                    dob=request.data.get('dob'),
                    position=line.current_count + 1
                )

                line.current_count += 1
                line.save()

            serializer = RegistrationSerializer(registration)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Line.DoesNotExist:
            raise NotFound("Queue not found")

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, pk=None):
        try:
            line = self.get_object()
            user = request.user

            with transaction.atomic():
                registration = Registration.objects.get(user=user, line=line)
                registration.delete()

                line.current_count = max(0, line.current_count - 1)
                line.save()

            return Response({"message": "Successfully left the queue."}, status=status.HTTP_200_OK)
        except Line.DoesNotExist:
            raise NotFound("Queue not found")
        except Registration.DoesNotExist:
            return Response({"error": "You are not in this queue."}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class RegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def my_queues(self, request):
        registrations = self.get_queryset()
        serializer = self.get_serializer(registrations, many=True)
        return Response(serializer.data)

