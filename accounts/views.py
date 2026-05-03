from rest_framework import viewsets, generics, permissions

from fraudlog.utils import increment_failed_login, reset_failed_login
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer
from .permissions import IsAdmin
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

# Create your views here.
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "end_user"
            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_blocked():
                messages.error(request, "Your account is temporarily locked due to multiple failed attempts.")
                return render(request, "accounts/login.html")

            login(request, user)
            reset_failed_login(user.id)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            count = increment_failed_login(username)
            ip_address = request.META.get("REMOTE_ADDR")
            device_info = request.META.get("HTTP_USER_AGENT")

            if count >= 3:
                try:
                    user = CustomUser.objects.get(username=username)
                    user.blocked_until = timezone.now() + timedelta(minutes=10)
                    user.save()
                except CustomUser.DoesNotExist:
                    pass

                from fraudlog.mongo_client import log_event
                log_event("failed_login_threshold", username, ip_address, device_info, extra={"attempts": count})
                messages.error(request, "Account temporarily locked due to multiple failed attempts.")
            else:
                messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")

