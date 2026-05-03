from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AccountViewSet, TransactionViewSet, account_detail, account_create, transaction_list, debit_create,
                    credit_request_create, credit_request_process, CreditRequestViewSet, CreditTransactionViewSet,
                    credit_request_list,my_credit_request_list)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'debit-transactions', TransactionViewSet, basename='debit-transaction')
router.register(r'credit-requests', CreditRequestViewSet, basename='credit-request')
router.register(r'credit-transactions', CreditTransactionViewSet, basename='credit-transaction')

urlpatterns = [
    path('', include(router.urls)),
    path("account/", account_detail, name="account_detail"),
    path("account/create/", account_create, name="account_create"),
    
    path("debit/new/", debit_create, name="debit_create"),
    
    path("transaction_list/", transaction_list, name="transaction_list"),
    
    path("credit/new/", credit_request_create, name="credit_request_create"),
    path("credit_request/list/", credit_request_list, name="credit_request_list"),
    path("my_credit_request/list/", my_credit_request_list, name="my_credit_request"),

    path("credit/approve/<int:pk>/", credit_request_process, name="credit_request_process"),
]
