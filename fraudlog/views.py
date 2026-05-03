from .models import FraudFlag
from .serializers import FraudFlagSerializer, FraudEventLogSerializer
from rest_framework import viewsets, filters
from .permissions import IsSupportOrAnalyst, IsAnalyst
from .mongo_client import get_events
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
from rest_framework.response import Response
from django.db.models import Count
from functools import wraps
from rest_framework.exceptions import PermissionDenied
from .forms import FraudResolveForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request.user, "role", None) not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class FraudFlagPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class FraudFlagViewSet(viewsets.ModelViewSet):
    serializer_class = FraudFlagSerializer
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

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            return [IsAnalyst()]
        elif self.action == "destroy":
            from rest_framework.permissions import IsAdminUser
            return [IsAdminUser()]
        return [IsSupportOrAnalyst()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().update(request, *args, **kwargs)

        if instance.resolved:
            if instance.transaction:
                instance.transaction.status = "at_support"
                instance.transaction.save()
            elif instance.credit_request:
                instance.credit_request.status = "at_support"
                instance.credit_request.save()

        return response

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



@login_required
def fraud_flags_ui(request):
    flags = FraudFlag.objects.all().order_by("-flagged_at")
    return render(request, "fraudlog/fraud_flags.html", {"flags": flags})

@login_required
def fraud_stats_ui(request):
    total_flags = FraudFlag.objects.count()
    resolved_flags = FraudFlag.objects.filter(resolved=True).count()
    unresolved_flags = total_flags - resolved_flags

    return render(request, "fraudlog/fraud_stats.html", {
        "total_flags": total_flags,
        "resolved_flags": resolved_flags,
        "unresolved_flags": unresolved_flags,
    })
    
@login_required
@role_required(["analyst"])
def resolve_fraud_flag(request, pk):
    flag = get_object_or_404(FraudFlag, pk=pk)

    if request.method == "POST":
        form = FraudResolveForm(request.POST, instance=flag)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.resolved = True
            flag.resolved_by = request.user
            flag.save()

            # Move linked object to support
            if flag.transaction:
                flag.transaction.status = "at_support"
                flag.transaction.save()
            elif flag.credit_request:
                flag.credit_request.status = "at_support"
                flag.credit_request.save()

            messages.success(request, "Fraud flag resolved and moved to support.")
            return redirect("fraud_flags_ui")
    else:
        form = FraudResolveForm(instance=flag)

    return render(request, "fraudlog/resolve_flag.html", {"form": form, "flag": flag})


