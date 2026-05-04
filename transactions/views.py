from decimal import Decimal

from django.http import Http404
from django.shortcuts import get_object_or_404, render

from fraudlog.mongo_client import log_event
from transactions.utils import check_transaction_velocity
from .models import Account, DebitTransaction, CreditRequest, CreditTransaction, ManualDebitTransaction, ReversalTransaction
from .serializers import (AccountSerializer, DebitTransactionSerializer, CreditRequestSerializer, 
                          CreditTransactionSerializer, ManualDebitTransactionSerializer, ReversalTransactionSerializer)
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from .permissions import IsEndUser, IsSupportOrAnalyst, IsAnalyst, IsSupport, IsAdminOrAnalyst
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import (DebitTransactionForm, CreditRequestForm, SupportCreditExecutionForm, SupportDebitExecutionForm, 
                    ManualDebitForm, ReversalForm, TransactionSearchForm)
from fraudlog.models import FraudFlag
from django.contrib import messages
from functools import wraps
from django.db.models import Q
from rest_framework import serializers



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
        if getattr(self, 'swagger_fake_view', False):
            return Account.objects.none()
        
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
        if getattr(self, 'swagger_fake_view', False):
            return Account.objects.none()
        
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
    manual_transactions = account.manul_transactions.filter(status="completed")
    reverse_transactions = account.reverse_transactions.filter(status="completed")
    
    transactions = list(debit_transactions) + list(credit_transactions)
    transactions.sort(key=lambda t: t.timestamp, reverse=True)
    
    transactions += list(manual_transactions) + list(reverse_transactions)
    
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


@login_required
@role_required(["support"])
def support_execute_debit(request, pk):
    transaction = get_object_or_404(DebitTransaction, pk=pk, status="at_support")
    if request.method == "POST":
        form = SupportDebitExecutionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            account = transaction.account
            dest_account = Account.objects.get(account_number=transaction.destination_account_number)

            account.balance -= transaction.amount
            dest_account.balance += transaction.amount
            account.save()
            dest_account.save()

            transaction.status = "completed"
            transaction.save()

            messages.success(request, "Debit transaction executed successfully.")
            return redirect("credit_request_list")
    else:
        form = SupportDebitExecutionForm(instance=transaction)

    return render(request, "transactions/support_execute_debit.html", {"form": form, "transaction": transaction})


@login_required
@role_required(["support"])
def support_execute_credit(request, pk):
    credit_request = get_object_or_404(CreditRequest, pk=pk, status="at_support")
    if request.method == "POST":
        form = SupportCreditExecutionForm(request.POST, instance=credit_request)
        if form.is_valid():
            credit_request = form.save(commit=False)
            account = credit_request.account
            
            account.balance += credit_request.amount
            account.save()

            CreditTransaction.objects.create(
                account=account,
                amount=credit_request.amount,
                deposit_reference=credit_request.deposit_reference,
                status="completed"
            )

            credit_request.status = "approved"
            credit_request.save()

            messages.success(request, "Credit request executed successfully.")
            return redirect("credit_request_list")
    else:
        form = SupportCreditExecutionForm(instance=credit_request)

    return render(request, "transactions/support_execute_credit.html", {"form": form, "credit_request": credit_request})

@login_required
@role_required(["analyst", "admin"])
def accounts_list(request):
    query = request.GET.get("q")
    if query:
        accounts = Account.objects.filter(Q(account_number__icontains=query))
    else:
        accounts = Account.objects.all()

    return render(request, "transactions/accounts_list.html", {"accounts": accounts, "query": query})

class ManualDebitTransactionViewSet(viewsets.ModelViewSet):
    queryset = ManualDebitTransaction.objects.all().order_by("-created_at")
    serializer_class = ManualDebitTransactionSerializer
    permission_classes = [IsAdminOrAnalyst]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        
@login_required
@role_required(["analyst", "admin"])
def manual_debit(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    if request.method == "POST":
        form = ManualDebitForm(request.POST)
        if form.is_valid():
            debit = form.save(commit=False)
            debit.account = account
            debit.created_by = request.user

            account.balance -= debit.amount
            account.save()

            debit.save()
            
            DebitTransaction.objects.create(
                account=account,
                destination_account_number=None,
                amount=debit.amount,
                description=f"Manual debit: {debit.reason}",
                status="completed"
            )
            
            messages.success(request, "Amount deducted successfully.")
            return redirect("accounts_list")
    else:
        form = ManualDebitForm()

    return render(request, "transactions/manual_debit.html", {
        "form": form,
        "account": account
    })

@login_required
@role_required(["analyst", "admin"])
def global_debit(request):
    if request.method == "POST":
        amount = Decimal(request.POST.get("amount"))
        reason = request.POST.get("reason")

        accounts = Account.objects.all()
        for account in accounts:
            account.balance -= amount
            account.save()

            ManualDebitTransaction.objects.create(
                account=account,
                amount=amount,
                reason=reason,
                created_by=request.user,
                is_global=True
            )
            
            DebitTransaction.objects.create(
                account=account,
                destination_account_number=None,
                amount=amount,
                description=f"Global debit: {reason}",
                status="completed"
            )

        messages.success(request, f"Global debit of {amount} applied to all accounts.")
        return redirect("accounts_list")

    return render(request, "transactions/global_debit.html")


@login_required
@role_required(["analyst", "admin"])
def all_transactions_list(request):
    form = TransactionSearchForm(request.GET or None)

    transactions = list(DebitTransaction.objects.all()) \
                + list(CreditTransaction.objects.all()) \
                + list(ManualDebitTransaction.objects.all())

    if form.is_valid():
        account_number = form.cleaned_data.get("account_number")
        transaction_id = form.cleaned_data.get("transaction_id")
        tx_type = form.cleaned_data.get("transaction_type")

        if tx_type and transaction_id:
            if tx_type == "debit":
                transactions = DebitTransaction.objects.filter(pk=transaction_id)
            elif tx_type == "credit":
                transactions = CreditTransaction.objects.filter(pk=transaction_id)
            elif tx_type == "manual":
                transactions = ManualDebitTransaction.objects.filter(pk=transaction_id)
        elif account_number:
            transactions = list(DebitTransaction.objects.filter(source_account__account_number=account_number)) \
                        + list(CreditTransaction.objects.filter(account__account_number=account_number)) \
                        + list(ManualDebitTransaction.objects.filter(account__account_number=account_number))

    return render(request, "transactions/all_transactions_list.html", {
        "form": form,
        "transactions": transactions
    })


@login_required
@role_required(["analyst", "admin"])
def reverse_transaction(request, tx_type, tx_id):
    if tx_type == "debit":
        original_tx = get_object_or_404(DebitTransaction, pk=tx_id)
        account = original_tx.source_account
    elif tx_type == "credit":
        original_tx = get_object_or_404(CreditTransaction, pk=tx_id)
        account = original_tx.account
    elif tx_type == "manual":
        original_tx = get_object_or_404(ManualDebitTransaction, pk=tx_id)
        account = original_tx.account
    else:
        raise Http404("Invalid transaction type")

    if original_tx.is_reversed:
        messages.error(request, "This transaction has already been reversed.")
        return redirect("all_transactions_list")

    if request.method == "POST":
        form = ReversalForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]

            if tx_type in ["debit", "manual"]:
                account.balance += original_tx.amount
            elif tx_type == "credit":
                account.balance -= original_tx.amount
            account.save()

            original_tx.is_reversed = True
            original_tx.save()

            ReversalTransaction.objects.create(
                debit_transaction=original_tx if tx_type == "debit" else None,
                credit_transaction=original_tx if tx_type == "credit" else None,
                manual_debit_transaction=original_tx if tx_type == "manual" else None,
                account=account,
                amount=original_tx.amount,
                reason=reason,
                created_by=request.user
            )

            if tx_type in ["debit", "manual"]:
                DebitTransaction.objects.create(
                    account=account,
                    destination_account_number=None,
                    amount=original_tx.amount,
                    description=f"Reversal of Transaction #{original_tx.id} – {reason}",
                    status="completed",
                    is_reversed=False
                )
            elif tx_type == "credit":
                CreditTransaction.objects.create(
                    account=account,
                    amount=original_tx.amount,
                    deposit_reference=f"Reversal of Transaction #{original_tx.id} – {reason}",
                    status="completed",
                    is_reversed=False
                )

            messages.success(request, "Transaction reversed successfully.")
            return redirect("all_transactions_list")
    else:
        form = ReversalForm()

    return render(request, "transactions/reverse_transaction.html", {
        "form": form,
        "transaction": original_tx,
        "tx_type": tx_type
    })


class ReversalTransactionViewSet(viewsets.ModelViewSet):
    queryset = ReversalTransaction.objects.all().order_by("-created_at")
    serializer_class = ReversalTransactionSerializer
    permission_classes = [IsAdminOrAnalyst]

    def perform_create(self, serializer):
        tx_type = self.request.data.get("tx_type")
        tx_id = self.request.data.get("tx_id")

        if tx_type == "debit":
            original_tx = get_object_or_404(DebitTransaction, pk=tx_id)
            account = original_tx.source_account
            account.balance += original_tx.amount
        elif tx_type == "credit":
            original_tx = get_object_or_404(CreditTransaction, pk=tx_id)
            account = original_tx.account
            account.balance -= original_tx.amount
        elif tx_type == "manual":
            original_tx = get_object_or_404(ManualDebitTransaction, pk=tx_id)
            account = original_tx.account
            account.balance += original_tx.amount
        else:
            raise serializers.ValidationError("Invalid transaction type")

        account.save()

        serializer.save(
            account=account,
            amount=original_tx.amount,
            created_by=self.request.user,
            debit_transaction=original_tx if tx_type == "debit" else None,
            credit_transaction=original_tx if tx_type == "credit" else None,
            manual_debit_transaction=original_tx if tx_type == "manual" else None,
        )


