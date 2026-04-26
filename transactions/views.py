from django.shortcuts import render
from .models import Account, Transaction, FraudFlag
from .serializers import AccountSerializer, TransactionSerializer, FraudFlagSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from .permissions import IsEndUser, IsSupportOrAnalyst


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

class FraudFlagViewSet(viewsets.ModelViewSet):
    serializer_class = FraudFlagSerializer
    permission_classes = [IsSupportOrAnalyst]
    
    def get_queryset(self):
        return FraudFlag.objects.all()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

