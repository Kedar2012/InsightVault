from rest_framework import serializers
from .models import Account, DebitTransaction, CreditRequest, CreditTransaction, ManualDebitTransaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'balance', 'created_at']
        read_only_fields = ['id', 'account_number', 'balance', 'created_at']

class DebitTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitTransaction
        fields = ["id", "account", "destination_account_number", "amount", "description", "status", "timestamp"]
        read_only_fields = ["status", "timestamp"]

class CreditRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRequest
        fields = ['id', 'account', 'amount', 'deposit_reference', 'status', 'created_at']


class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['id', 'account', 'amount', 'deposit_reference', 'status', 'timestamp']

class ManualDebitTransactionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = ManualDebitTransaction
        fields = ["id", "account", "amount", "reason", "created_by", "created_at", "status", "is_global"]
        read_only_fields = ["created_by", "created_at", "status"]

