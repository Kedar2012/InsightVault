from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FraudFlagViewSet, FraudEventLogViewSet

router = DefaultRouter()
router.register(r'fraudflags', FraudFlagViewSet, basename='fraudflag')
router.register(r'fraudevents', FraudEventLogViewSet, basename='fraudevent')

urlpatterns = [
    path('', include(router.urls)),
]
