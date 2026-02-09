from rest_framework import viewsets,generics
from .models import Customer,LedgerEntry
from .serializers import CustomerSerializer,LedgerEntrySerializer
from rest_framework.exceptions import NotFound,ValidationError
from datetime import date
from typing import Optional
from decimal  import Decimal
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LedgerEntryViewSet(viewsets.ModelViewSet):
    serializer_class = LedgerEntrySerializer

    def get_queryset(self):
        qs = (
            LedgerEntry.objects.filter(user=self.request.user)
            .select_related("customer")
        )
        return apply_entry_filters(self.request, qs)


class CustomerEntriesListView(generics.ListAPIView):
    serializer_class = LedgerEntrySerializer

    def get_queryset(self):
        customer_id = self.kwargs["customer_id"]

        customer_exists = Customer.objects.filter(
            id=customer_id,
            user=self.request.user,
        ).exists()

        if not customer_exists:
            raise NotFound("Customer not found.")

        qs = (
            LedgerEntry.objects.filter(
                user=self.request.user,
                customer_id=customer_id,
            )
            .select_related("customer")
        )
        return apply_entry_filters(self.request, qs)


def _parse_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError({field_name: "Invalid date format. Use YYYY-MM-DD."}) from exc


def apply_entry_filters(request, queryset):
    """
    Supported query params:
      - start_date=YYYY-MM-DD
      - end_date=YYYY-MM-DD
      - type=credit|debit
    """
    start_date_str: Optional[str] = request.query_params.get("start_date")
    end_date_str: Optional[str] = request.query_params.get("end_date")
    entry_type: Optional[str] = request.query_params.get("type")

    if entry_type:
        if entry_type not in ("credit", "debit"):
            raise ValidationError({"type": "Invalid type. Use 'credit' or 'debit'."})
        queryset = queryset.filter(entry_type=entry_type)

    if start_date_str:
        start = _parse_date(start_date_str, "start_date")
        queryset = queryset.filter(date__gte=start)

    if end_date_str:
        end = _parse_date(end_date_str, "end_date")
        queryset = queryset.filter(date__lte=end)

    return queryset

class CustomerSummaryView(APIView):
    def get(self, request, customer_id: int):
        customer_exists = Customer.objects.filter(
            id=customer_id,
            user=request.user,
        ).exists()

        if not customer_exists:
            raise NotFound("Customer not found.")

        totals = (
            LedgerEntry.objects.filter(user=request.user, customer_id=customer_id)
            .values("entry_type")
            .annotate(total=Sum("amount"))
        )

        total_credit = Decimal("0.00")
        total_debit = Decimal("0.00")

        for row in totals:
            if row["entry_type"] == "credit":
                total_credit = row["total"] or Decimal("0.00")
            elif row["entry_type"] == "debit":
                total_debit = row["total"] or Decimal("0.00")

        balance = total_credit - total_debit

        return Response(
            {
                "total_credit": f"{total_credit:.2f}",
                "total_debit": f"{total_debit:.2f}",
                "balance": f"{balance:.2f}",
            }
        )