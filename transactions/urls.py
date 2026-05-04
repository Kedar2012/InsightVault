from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AccountViewSet, TransactionViewSet, account_detail, account_create, transaction_list, 
                    debit_create, credit_request_create, credit_request_process, CreditRequestViewSet, 
                    CreditTransactionViewSet, credit_request_list, my_credit_request_list, 
                    support_execute_debit, support_execute_credit, ManualDebitTransactionViewSet, 
                    manual_debit, global_debit, accounts_list, reverse_transaction, ReversalTransactionViewSet, 
                    all_transactions_list)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'debit-transactions', TransactionViewSet, basename='debit-transaction')
router.register(r'credit-requests', CreditRequestViewSet, basename='credit-request')
router.register(r'credit-transactions', CreditTransactionViewSet, basename='credit-transaction')
router.register(r'manual-debits', ManualDebitTransactionViewSet, basename='manual-debit')
router.register(r'reversals', ReversalTransactionViewSet, basename='reversal')


urlpatterns = [
    path('', include(router.urls)),

    # End-user account + transaction routes
    path("account/", account_detail, name="account_detail"),
    path("account/create/", account_create, name="account_create"),
    path("debit/new/", debit_create, name="debit_create"),
    path("transaction_list/", transaction_list, name="transaction_list"),
    path("credit/new/", credit_request_create, name="credit_request_create"),
    path("my_credit_request/list/", my_credit_request_list, name="my_credit_request"),

    # Analyst/support shared list
    path("credit_request/list/", credit_request_list, name="credit_request_list"),
    path("credit/approve/<int:pk>/", credit_request_process, name="credit_request_process"),
    path("accounts/<int:account_id>/manual-debit/", manual_debit, name="manual_debit"),
    path("accounts_list/manual_debit", accounts_list, name="accounts_list"),
    path("global-debit/", global_debit, name="global_debit"),
    path("reverse_transactions/<str:tx_type>/<int:tx_id>/reverse/", reverse_transaction, name="reverse_transaction"),
    path("all_transactions_list/", all_transactions_list, name="all_transactions_list"),
    
    # Support-only execution routes
    path("support/debit/<int:pk>/execute/", support_execute_debit, name="support_execute_debit"),
    path("support/credit/<int:pk>/execute/", support_execute_credit, name="support_execute_credit"),
]

