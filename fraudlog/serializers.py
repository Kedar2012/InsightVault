from rest_framework import serializers
from .models import FraudFlag
      
class FraudFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudFlag
        fields = ['transaction','reason','resolved']
        read_only_fields = ('resolved', 'flagged_at')

# class FraudEventLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FraudEventLog
#         fields = ['user', 'event_type', 'details', 'created_at']
#         read_only_fields = ('created_at',)


class FraudEventLogSerializer(serializers.Serializer):
    event_type = serializers.CharField()
    user_id = serializers.CharField()
    ip_address = serializers.CharField(required=False)
    device_info = serializers.CharField(required=False)
    severity = serializers.CharField(required=False)
    reason = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField()
    extra = serializers.JSONField(required=False)

