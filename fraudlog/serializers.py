from rest_framework import serializers
from .models import FraudFlag, FraudEventLog
      
class FraudFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudFlag
        fields = ['transaction','reason','resolved']
        read_only_fields = ('resolved', 'flagged_at')

class FraudEventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudEventLog
        fields = ['user', 'event_type', 'details', 'created_at']
        read_only_fields = ('created_at',)

