from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.utils import timezone
from accounts.decorators import admin_required
from products.models import Product
from billing.models import Sale


@login_required
@admin_required
def home(request):
    today = timezone.now().date()
    today_sales = Sale.objects.filter(created_at__date=today, payment_status="COMPLETED")
    today_revenue = today_sales.aggregate(total=Sum("grand_total"))["total"] or 0
    today_orders = today_sales.count()
    total_products = Product.objects.filter(is_active=True).count()
    low_stock = Product.objects.filter(
        is_active=True, stock_quantity__lte=F("reorder_level")
    ).count()

    recent_sales = Sale.objects.select_related("staff").order_by("-created_at")[:8]

    context = {
        "today_revenue": today_revenue,
        "today_orders": today_orders,
        "total_products": total_products,
        "low_stock": low_stock,
        "recent_sales": recent_sales,
    }
    return render(request, "dashboard/dashboard.html", context)