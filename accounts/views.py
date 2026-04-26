from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer
from .permissions import IsAdmin

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

