import pytest
from transactions.models import Account, DebitTransaction, CreditRequest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_debit_transaction_creation():
    user = User.objects.create_user(username="testuser", password="pass123")
    account = Account.objects.create(user=user)

    tx = DebitTransaction.objects.create(
        account=account,
        destination_account_number="1234567890",
        amount=500,
        description="Test debit"
    )

    assert tx.amount == 500
    assert tx.transaction_type == "Debit"
    assert tx.status == "completed"

@pytest.mark.django_db
def test_credit_request_creation():
    user = User.objects.create_user(username="testuser2", password="pass123")
    account = Account.objects.create(user=user)

    cr = CreditRequest.objects.create(
        account=account,
        amount=1000,
        deposit_reference="REF123"
    )

    assert cr.amount == 1000
    assert cr.status == "pending"
