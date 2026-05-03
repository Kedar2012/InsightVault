from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FraudFlagViewSet, FraudEventLogViewSet, FraudStatsViewSet, resolve_fraud_flag, fraud_flags_ui, fraud_stats_ui

router = DefaultRouter()
router.register(r'fraudflags', FraudFlagViewSet, basename='fraudflag')
router.register(r'fraud-events', FraudEventLogViewSet, basename='fraud-events')
router.register(r'stats', FraudStatsViewSet, basename='fraud-stats')

urlpatterns = [
    path('', include(router.urls)),
    path("fraudflags_ui/", fraud_flags_ui, name="fraud_flags_ui"),
    path("fraudstats_ui/", fraud_stats_ui, name="fraud_stats_ui"),
    path("fraudflags/<int:pk>/resolve/", resolve_fraud_flag, name="resolve_fraud_flag"),
]
