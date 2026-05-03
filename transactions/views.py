from django.shortcuts import get_object_or_404, render

from fraudlog.mongo_client import log_event
from transactions.utils import check_transaction_velocity
from .models import Account, DebitTransaction, CreditRequest, CreditTransaction
from .serializers import AccountSerializer, DebitTransactionSerializer, CreditRequestSerializer, CreditTransactionSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from .permissions import IsEndUser, IsSupportOrAnalyst
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import DebitTransactionForm, CreditRequestForm
from fraudlog.models import FraudFlag
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request.user, "role", None) not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

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
    serializer_class = DebitTransactionSerializer
    permission_classes = [IsEndUser]
    
    def get_queryset(self):
        user = self.request.user
        return DebitTransaction.objects.filter(account__user=user)

    def perform_create(self, serializer):
        account = serializer.validated_data['account']
        if account.user != self.request.user:
            raise PermissionDenied("You cannot create transactions for another user's account.")
        serializer.save()

@login_required
@role_required(["end_user"])
def account_detail(request):
    try:
        account = Account.objects.get(user=request.user)
    except Account.DoesNotExist:
        return redirect("account_create")
    return render(request, "transactions/account_detail.html", {"account": account})

@login_required
@role_required(["end_user"])
def account_create(request):
    if Account.objects.filter(user=request.user).exists():
        return redirect("account_detail")
    Account.objects.create(user=request.user)
    return redirect("account_detail")

@login_required
@role_required(["end_user"])
def transaction_list(request):
    account = Account.objects.get(user=request.user)

    debit_transactions = account.debit_transactions.filter(status="completed")
    credit_transactions = account.credit_transactions.filter(status__in=["completed", "rejected"])

    transactions = list(debit_transactions) + list(credit_transactions)
    transactions.sort(key=lambda t: t.timestamp, reverse=True)

    return render(
        request,
        "transactions/transaction_list.html",
        {"transactions": transactions}
    )


@login_required
@role_required(["end_user"])
def debit_create(request):
    account = request.user.account
    bal = account.balance
    if request.method == "POST":
        form = DebitTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            
            dest_acc_no = transaction.destination_account_number
            try:
                dest_account = Account.objects.get(account_number=dest_acc_no)
            except Account.DoesNotExist:
                messages.error(request, "Destination account does not exist.")
                return render(request, "transactions/debit_create.html", {"form": form})
                
            if dest_account == account:
                messages.error(request, "You cannot transfer to your own account.")
                return render(request, "transactions/debit_create.html", {"form": form})

            if account.balance < transaction.amount:
                messages.error(request, "Insufficient balance for transfer.")
                return render(request, "transactions/debit_create.html", {"form": form})
            
            account.balance -= transaction.amount
            dest_account.balance += transaction.amount
            account.save()
            dest_account.save()
                
            transaction.save()
            
            if check_transaction_velocity(account.id):
                FraudFlag.objects.create(
                    transaction=transaction,
                    reason="Velocity check failed (too many debits in 1 min)",
                    severity="high"
                )
                transaction.status = "fraud_blocked"
                transaction.save(update_fields=["status"])
                account.balance = bal
                account.save()
                dest_account.balance -= transaction.amount
                dest_account.save()

                log_event(
                    event_type="velocity_check",
                    user_id=request.user.id,
                    extra={"reason": "Too many debits in 1 minute"}
                )

                messages.error(request, "Transaction blocked due to velocity fraud rule.")
                return render(request, "transactions/debit_create.html", {"form": form})
            
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
                dest_account.balance -= transaction.amount
                dest_account.save()
                
                messages.error(request, "Transaction blocked due to fraud suspicion.")
                return render(request, "transactions/debit_create.html", {"form": form})

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
                dest_account.balance -= transaction.amount
                dest_account.save()
                
                messages.error(request, "Transaction blocked due to insufficient balance.")
                return render(request, "transactions/debit_create.html", {"form": form})

            messages.success(request, "Transaction completed successfully.")
            return redirect("transaction_list")
    else:
        form = DebitTransactionForm()
    return render(request, "transactions/debit_create.html", {"form": form})


@login_required
@role_required(["end_user"])
def credit_request_create(request):
    account = request.user.account
    if request.method == "POST":
        form = CreditRequestForm(request.POST)
        if form.is_valid():
            credit_request = form.save(commit=False)
            credit_request.account = account

            if check_transaction_velocity(account.id):
                credit_request.status = "fraud_blocked"
                credit_request.fraud = True
                credit_request.save()
                
                FraudFlag.objects.create(
                    reason="Velocity check failed (too many credit requests in 1 min)",
                    severity="high",
                    credit_request=credit_request
                )

                log_event(
                    event_type="velocity_check",
                    user_id=request.user.id,
                    extra={"reason": "Too many credit requests in 1 minute"}
                )
                
                messages.error(request, "Credit request blocked due to velocity fraud rule.")
                return redirect("my_credit_request")

            if credit_request.amount > 100000:
                credit_request.status = "fraud_blocked"
                credit_request.fraud = True
                credit_request.save()
                
                FraudFlag.objects.create(
                    reason="High value credit request blocked",
                    severity="high",
                    credit_request=credit_request
                )

                log_event(
                    event_type="high_value_credit",
                    user_id=request.user.id,
                    extra={"amount": str(credit_request.amount)}
                )
                
                messages.error(request, "Credit request blocked due to high value fraud rule.")
                return redirect("my_credit_request")

            credit_request.save()
            messages.success(request, "Credit request submitted successfully.")
            return redirect("my_credit_request")
    else:
        form = CreditRequestForm()
    return render(request, "transactions/credit_request_create.html", {"form": form})


@login_required
@role_required(["analyst", "support"])
def credit_request_process(request, pk):
    credit_request = get_object_or_404(CreditRequest, pk=pk)

    if credit_request.status != "pending":
        messages.error(request, "This request has already been processed.")
        return redirect("credit_request_list")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve":
            if credit_request.fraud:
                messages.error(request, "This request is flagged as fraud and cannot be approved.")
                return redirect("credit_request_list")

            account = credit_request.account
            credit_tx = CreditTransaction.objects.create(
                account=account,
                amount=credit_request.amount,
                deposit_reference=credit_request.deposit_reference,
                status="completed"
            )

            credit_request.status = "approved"
            credit_request.save()
            messages.success(request, "Credit request approved and transaction completed.")

        elif action == "reject":
            credit_request.status = "rejected"
            credit_request.save()
            messages.warning(request, "Credit request rejected.")

        return redirect("credit_request_list")

    return render(
        request,
        "transactions/credit_request_process.html",
        {"credit_request": credit_request}
    )


@login_required
@role_required(["analyst", "support"])
def credit_request_list(request):
    credit_requests = CreditRequest.objects.all().order_by("-created_at")
    return render(request, "transactions/credit_request_list.html", {"credit_requests": credit_requests})


@login_required
@role_required(["end_user"])
def my_credit_request_list(request):
    credit_requests = CreditRequest.objects.filter(account=request.user.account).order_by("-created_at")
    return render(request, "transactions/my_credit_request_list.html", {"credit_requests": credit_requests})

class CreditRequestViewSet(viewsets.ModelViewSet):
    queryset = CreditRequest.objects.all()
    serializer_class = CreditRequestSerializer
    permission_classes = [IsEndUser]

class CreditTransactionViewSet(viewsets.ModelViewSet):
    queryset = CreditTransaction.objects.all()
    serializer_class = CreditTransactionSerializer
    permission_classes = [IsSupportOrAnalyst]

