from django.shortcuts import render
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from .permissions import IsEndUser, IsSupportOrAnalyst
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Account, Transaction
from .forms import TransactionForm
from fraudlog.models import FraudFlag
from django.contrib import messages

class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsEndUser]
    
    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)        

    def perform_create(self, serializer):
        if Account.objects.filter(user=self.request.user).exists():
            raise PermissionDenied("You already have an account.")
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsEndUser]
    
    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(account__user=user)

    def perform_create(self, serializer):
        account = serializer.validated_data['account']
        if account.user != self.request.user:
            raise PermissionDenied("You cannot create transactions for another user's account.")
        serializer.save()

@login_required
def account_detail(request):
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        return redirect("account_create")
    return render(request, "transactions/account_detail.html", {"account": account})

@login_required
def account_create(request):
    if Account.objects.filter(user=request.user).exists():
        return redirect("account_detail")
    Account.objects.create(user=request.user)
    return redirect("account_detail")

@login_required
def transaction_list(request):
    account = Account.objects.get(user=request.user)
    transactions = account.transactions.all()
    return render(request, "transactions/transaction_list.html", {"transactions": transactions})

@login_required
def transaction_create(request):
    account = request.user.account
    bal = account.balance
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.save()

            if transaction.amount > 100000:
                FraudFlag.objects.create(
                    transaction=transaction,
                    reason="High value transaction blocked",
                    severity="high"
                )
                transaction.status = "fraud_blocked"
                transaction.save(update_fields=["status"])
                account.balance = bal
                account.save()
                messages.error(request, "Transaction blocked due to fraud suspicion.")
                return redirect("transaction_list")

            if account.balance < 0:
                FraudFlag.objects.create(
                    transaction=transaction,
                    reason="Overdraft attempt blocked",
                    severity="high"
                )
                transaction.status = "fraud_blocked"
                transaction.save(update_fields=["status"])
                account.balance = bal
                account.save()
                messages.error(request, "Transaction blocked due to insufficient balance.")
                return redirect("transaction_list")

            messages.success(request, "Transaction completed successfully.")
            return redirect("transaction_list")
    else:
        form = TransactionForm()
    return render(request, "transactions/transaction_create.html", {"form": form})

