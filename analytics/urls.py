from django.urls import path
from .views import TransactionSummaryView, FraudFlagSummaryView

urlpatterns = [
    path("transactions/summary/", TransactionSummaryView.as_view(), name="transaction-summary"),
    path("fraud/flags/", FraudFlagSummaryView.as_view(), name="fraud-flag-summary"),
]
