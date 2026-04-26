from django.shortcuts import render
from .models import Account, Transaction, FraudFlag
from .serializers import AccountSerializer, TransactionSerializer, FraudFlagSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from .permissions import IsEndUser, IsSupportOrAnalyst


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsEndUser]   # only end users

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsEndUser]   # only end users

    def perform_create(self, serializer):
        account = serializer.validated_data['account']
        if account.user != self.request.user:
            raise PermissionDenied("You cannot create transactions for another user's account.")
        serializer.save()


class FraudFlagViewSet(viewsets.ModelViewSet):
    queryset = FraudFlag.objects.all()
    serializer_class = FraudFlagSerializer
    permission_classes = [IsSupportOrAnalyst]   # only support/analyst

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


