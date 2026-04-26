from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, TransactionViewSet, FraudFlagViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'fraudflags', FraudFlagViewSet, basename='fraudflag')

urlpatterns = [
    path('', include(router.urls)),
]
