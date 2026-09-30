from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.decorators import admin_required
from billing.models import Sale, SaleItem
from products.models import Product
from returns.models import Return
from ledger.models import LedgerEntry


@login_required
@admin_required
def reports_home(request):
    return render(request, "reports/home.html")


@login_required
@admin_required
def sales_report(request):
    period = request.GET.get("period", "7")  # days
    try:
        days = int(period)
    except ValueError:
        days = 7

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    sales = Sale.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        payment_status="COMPLETED"
    )

    # Totals
    total_sales = sales.aggregate(total=Sum("grand_total"))["total"] or Decimal("0")
    total_orders = sales.count()
    total_discount = sales.aggregate(total=Sum("discount"))["total"] or Decimal("0")

    # Payment method breakdown
    payment_breakdown = (
        sales.values("payment_method")
        .annotate(count=Count("id"), amount=Sum("grand_total"))
        .order_by("-amount")
    )

    # Daily sales for chart
    daily = (
        sales.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("grand_total"), orders=Count("id"))
        .order_by("day")
    )

    # Top products
    top_products = (
        SaleItem.objects.filter(sale__in=sales)
        .values("product__name", "product__sku")
        .annotate(qty=Sum("quantity"), revenue=Sum("total"))
        .order_by("-revenue")[:10]
    )

    context = {
        "period": days,
        "start_date": start_date,
        "end_date": end_date,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_discount": total_discount,
        "avg_order": total_sales / total_orders if total_orders else 0,
        "payment_breakdown": payment_breakdown,
        "daily": list(daily),
        "top_products": top_products,
    }
    return render(request, "reports/sales.html", context)


@login_required
@admin_required
def inventory_report(request):
    products = Product.objects.filter(is_active=True).select_related("category", "supplier")

    total_products = products.count()
    low_stock = products.filter(stock_quantity__lte=F("reorder_level")).count()
    out_of_stock = products.filter(stock_quantity=0).count()
    total_stock_value = products.aggregate(
        value=Sum(F("stock_quantity") * F("purchase_price"))
    )["value"] or Decimal("0")
    potential_revenue = products.aggregate(
        value=Sum(F("stock_quantity") * F("selling_price"))
    )["value"] or Decimal("0")

    low_stock_products = products.filter(
        stock_quantity__lte=F("reorder_level")
    ).order_by("stock_quantity")[:20]

    # Category wise
    by_category = (
        products.values("category__name")
        .annotate(
            count=Count("id"),
            stock=Sum("stock_quantity"),
            value=Sum(F("stock_quantity") * F("purchase_price"))
        )
        .order_by("-count")
    )

    context = {
        "total_products": total_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_stock_value": total_stock_value,
        "potential_revenue": potential_revenue,
        "low_stock_products": low_stock_products,
        "by_category": by_category,
    }
    return render(request, "reports/inventory.html", context)


@login_required
@admin_required
def profit_report(request):
    period = request.GET.get("period", "30")
    try:
        days = int(period)
    except ValueError:
        days = 30

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    # Sales in period
    sales = Sale.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        payment_status="COMPLETED"
    )
    total_revenue = sales.aggregate(total=Sum("grand_total"))["total"] or Decimal("0")

    # Cost of goods sold (approximate using purchase_price)
    sale_items = SaleItem.objects.filter(sale__in=sales).select_related("product")
    cogs = Decimal("0")
    for item in sale_items:
        cogs += item.product.purchase_price * item.quantity

    # Returns in period
    returns = Return.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status="APPROVED"
    )
    total_returns = returns.aggregate(total=Sum("refund_amount"))["total"] or Decimal("0")

    gross_profit = total_revenue - cogs - total_returns
    margin = (gross_profit / total_revenue * 100) if total_revenue else 0

    context = {
        "period": days,
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": total_revenue,
        "cogs": cogs,
        "total_returns": total_returns,
        "gross_profit": gross_profit,
        "margin": margin,
    }
    return render(request, "reports/profit.html", context)