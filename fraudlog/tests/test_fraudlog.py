import pytest
from fraudlog.models import FraudFlag
from transactions.models import Account, DebitTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_fraud_flag_creation():
    user = User.objects.create_user(username="frauduser", password="pass123")
    account = Account.objects.create(user=user)

    tx = DebitTransaction.objects.create(account=account, amount=100)

    flag = FraudFlag.objects.create(
        transaction=tx,
        reason="Suspicious activity",
        resolved=False
    )

    assert flag.reason == "Suspicious activity"
    assert flag.resolved is False
