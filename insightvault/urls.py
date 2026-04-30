from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.Home, name='home'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('api/accounts/', include('accounts.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/fraudlog/', include('fraudlog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
