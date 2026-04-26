from .models import FraudFlag, FraudEventLog
from .serializers import FraudFlagSerializer, FraudEventLogSerializer
from rest_framework import viewsets
from .permissions import IsSupportOrAnalyst


class FraudFlagViewSet(viewsets.ModelViewSet):
    serializer_class = FraudFlagSerializer
    permission_classes = [IsSupportOrAnalyst]
    
    def get_queryset(self):
        return FraudFlag.objects.all()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class FraudEventLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FraudEventLog.objects.all().order_by('-created_at')
    serializer_class = FraudEventLogSerializer

