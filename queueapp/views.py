from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from .models import Line, Registration
from .serializers import UserSerializer, LineSerializer, RegistrationSerializer
from django.contrib.auth.models import User

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
        })

    @action(detail=False, methods=['POST'])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def logout(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({"success": "Successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "You're not logged in."}, status=status.HTTP_400_BAD_REQUEST)

class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pincode']
    search_fields = ['name']

    @action(detail=True, methods=['POST'])
    def register(self, request, pk=None):
        line = self.get_object()
        if line.current_count >= line.capacity:
            return Response({"error": "This line is full."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, line=line, position=line.current_count + 1)
            line.current_count += 1
            line.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def leave(self, request, pk=None):
        line = self.get_object()
        try:
            registration = Registration.objects.get(user=request.user, line=line)
            registration.delete()
            line.current_count -= 1
            line.save()
            return Response({"success": "Successfully left the line."}, status=status.HTTP_200_OK)
        except Registration.DoesNotExist:
            return Response({"error": "You are not registered in this line."}, status=status.HTTP_400_BAD_REQUEST)

class RegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user)

