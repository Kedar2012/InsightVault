from .models import FraudFlag
from .serializers import FraudFlagSerializer, FraudEventLogSerializer
from rest_framework import viewsets, filters
from .permissions import IsSupportOrAnalyst
from .mongo_client import get_events
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
from rest_framework.response import Response
from django.db.models import Count

class FraudFlagPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class FraudFlagViewSet(viewsets.ModelViewSet):
    serializer_class = FraudFlagSerializer
    permission_classes = [IsSupportOrAnalyst]
    pagination_class = FraudFlagPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["flagged_at", "severity", "resolved"]
    search_fields = ["reason"]
    
    def get_queryset(self):
        qs = FraudFlag.objects.all()
        severity = self.request.query_params.get("severity")
        resolved = self.request.query_params.get("resolved")
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        
        if severity:
            qs = qs.filter(severity=severity)
        if resolved is not None:
            qs = qs.filter(resolved=(resolved.lower() == "true"))
        if from_date and to_date:
            qs = qs.filter(flagged_at__range=[from_date, to_date])
        elif from_date:
            qs = qs.filter(flagged_at__gte=from_date)
        elif to_date:
            qs = qs.filter(flagged_at__lte=to_date)
            
        return qs.order_by("-flagged_at")

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

# class FraudEventLogViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = FraudEventLog.objects.all().order_by('-created_at')
#     serializer_class = FraudEventLogSerializer

class FraudEventLogViewSet(viewsets.ViewSet):
    permission_classes = [IsSupportOrAnalyst]
    pagination_class = FraudFlagPagination
    
    def list(self,request):
        query = {}
        severity = request.query_params.get("severity")
        user_id = request.query_params.get("user_id")
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        
        if severity:
            query["severity"] = severity
        if user_id:
            query["user_id"] = user_id
        
        if from_date or to_date:
            query["timestamp"] = {}
            if from_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(from_date)
            if to_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(to_date)
    
        events = get_events(query)
        events = sorted(events, key=lambda e: e.get("timestamp"), reverse=True)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(events, request)
        serializer = FraudEventLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class FraudStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsSupportOrAnalyst]

    def list(self, request):
        # --- Postgres FraudFlag stats ---
        flag_stats = (
            FraudFlag.objects.values("severity")
            .annotate(count=Count("id"))
            .order_by("severity")
        )

        query = {}
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date or to_date:
            query["timestamp"] = {}
            if from_date:
                query["timestamp"]["$gte"] = datetime.fromisoformat(from_date)
            if to_date:
                query["timestamp"]["$lte"] = datetime.fromisoformat(to_date)

        events = get_events(query)

        event_stats = {}
        for e in events:
            sev = e.get("severity", "unknown")
            event_stats[sev] = event_stats.get(sev, 0) + 1

        return Response({
            "fraud_flags": list(flag_stats),
            "fraud_events": event_stats
        })

