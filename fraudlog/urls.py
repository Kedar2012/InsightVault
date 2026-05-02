from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FraudFlagViewSet, FraudEventLogViewSet, FraudStatsViewSet

router = DefaultRouter()
router.register(r'fraudflags', FraudFlagViewSet, basename='fraudflag')
router.register(r'fraud-events', FraudEventLogViewSet, basename='fraud-events')
router.register(r'stats', FraudStatsViewSet, basename='fraud-stats')

urlpatterns = [
    path('', include(router.urls)),
]
