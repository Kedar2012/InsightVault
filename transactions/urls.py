from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, TransactionViewSet, account_detail, account_create, transaction_list, transaction_create

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path("account/", account_detail, name="account_detail"),
    path("account/create/", account_create, name="account_create"),
    path("transaction_list/", transaction_list, name="transaction_list"),
    path("transaction_create/", transaction_create, name="transaction_create"),
]
