from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.decorators import admin_required
from .models import LedgerEntry


@login_required
@admin_required
def ledger_list(request):
    q = request.GET.get("q", "").strip()
    entry_type = request.GET.get("type", "")
    date_from = request.GET.get("from", "")
    date_to = request.GET.get("to", "")

    entries = LedgerEntry.objects.all().order_by("-created_at")

    if q:
        entries = entries.filter(
            Q(reference__icontains=q) |
            Q(description__icontains=q)
        )

    if entry_type:
        entries = entries.filter(entry_type=entry_type)

    if date_from:
        entries = entries.filter(created_at__date__gte=date_from)

    if date_to:
        entries = entries.filter(created_at__date__lte=date_to)

    # Summary cards
    total_credit = entries.aggregate(total=Sum("credit"))["total"] or Decimal("0")
    total_debit = entries.aggregate(total=Sum("debit"))["total"] or Decimal("0")
    current_balance = entries.first().balance if entries.exists() else Decimal("0")

    # Today's summary
    today = timezone.now().date()
    today_entries = LedgerEntry.objects.filter(created_at__date=today)
    today_credit = today_entries.aggregate(total=Sum("credit"))["total"] or Decimal("0")
    today_debit = today_entries.aggregate(total=Sum("debit"))["total"] or Decimal("0")

    context = {
        "entries": entries[:200],  # limit for performance
        "q": q,
        "entry_type": entry_type,
        "date_from": date_from,
        "date_to": date_to,
        "total_credit": total_credit,
        "total_debit": total_debit,
        "current_balance": current_balance,
        "today_credit": today_credit,
        "today_debit": today_debit,
        "type_choices": LedgerEntry.TYPE_CHOICES,
    }
    return render(request, "ledger/ledger.html", context)