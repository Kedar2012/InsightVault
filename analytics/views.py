from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from transactions.models import DebitTransaction, CreditTransaction, ManualDebitTransaction, ReversalTransaction
from fraudlog.models import FraudFlag
from .serializers import TransactionSummarySerializer, FraudFlagSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAnalystOrAdmin

class TransactionSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAnalystOrAdmin]
    def get(self, request):
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        account = request.GET.get("account")

        filters = {}
        if date_from:
            filters["created_at__gte"] = parse_date(date_from)
        if date_to:
            filters["created_at__lte"] = parse_date(date_to)
        if account:
            filters["account__account_number"] = account

        summaries = []

        debit_summary = DebitTransaction.objects.filter(**filters).aggregate(
            count=Count("id"), total_amount=Sum("amount")
        )
        summaries.append({"type": "debit", **debit_summary})

        credit_summary = CreditTransaction.objects.filter(**filters).aggregate(
            count=Count("id"), total_amount=Sum("amount")
        )
        summaries.append({"type": "credit", **credit_summary})

        manual_summary = ManualDebitTransaction.objects.filter(**filters).aggregate(
            count=Count("id"), total_amount=Sum("amount")
        )
        summaries.append({"type": "manual/global", **manual_summary})

        reversal_summary = ReversalTransaction.objects.filter(**filters).aggregate(
            count=Count("id"), total_amount=Sum("amount")
        )
        summaries.append({"type": "reversal", **reversal_summary})

        serializer = TransactionSummarySerializer(summaries, many=True)
        return Response(serializer.data)


class FraudFlagSummaryView(APIView):
    permission_classes = [IsAuthenticated, IsAnalystOrAdmin]
    def get(self, request):
        fraud_summary = FraudFlag.objects.values("severity").annotate(
            count=Count("id")
        )

        data = [
            {"account": "ALL", "severity": item["severity"], "count": item["count"]}
            for item in fraud_summary
        ]
        serializer = FraudFlagSerializer(data, many=True)
        return Response(serializer.data)
