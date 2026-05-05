from rest_framework import serializers

class TransactionSummarySerializer(serializers.Serializer):
    type = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class FraudFlagSerializer(serializers.Serializer):
    account = serializers.CharField()
    severity = serializers.CharField()
    count = serializers.IntegerField()
    
