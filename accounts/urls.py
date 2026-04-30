from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterView, register, login_view, logout_view

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("api/register/", RegisterView.as_view(), name="api-register"),
    path("", include(router.urls)),
]
