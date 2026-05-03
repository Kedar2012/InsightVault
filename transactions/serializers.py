from rest_framework import serializers
from .models import Account, DebitTransaction, CreditRequest, CreditTransaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'balance', 'created_at']
        read_only_fields = ['id', 'account_number', 'balance', 'created_at']

class DebitTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitTransaction
        fields = ['account', 'destination_account_number', 'amount', 'description']

class CreditRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRequest
        fields = ['id', 'account', 'amount', 'deposit_reference', 'status', 'created_at']


class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['id', 'account', 'amount', 'deposit_reference', 'status', 'timestamp']

