from rest_framework import serializers
from .models import Account, FraudFlag, Transaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['user']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['account','amount','transaction_type','description']
        
class FraudFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudFlag
        fields = ['transaction','reason','resolved']
        read_only_fields = ('resolved', 'flagged_at')

