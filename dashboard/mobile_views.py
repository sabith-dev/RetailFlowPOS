from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count, Q
from django.utils import timezone
from accounts.decorators import admin_required
from products.models import Product
from billing.models import Sale
from suppliers.models import Supplier
from returns.models import Return
from accounts.models import StaffProfile
from ledger.models import LedgerEntry


@login_required
@admin_required
def mobile_home(request):
    today = timezone.now().date()
    today_sales = Sale.objects.filter(created_at__date=today, payment_status="COMPLETED")
    today_revenue = today_sales.aggregate(total=Sum("grand_total"))["total"] or 0
    today_orders = today_sales.count()
    total_products = Product.objects.filter(is_active=True).count()
    low_stock = Product.objects.filter(is_active=True, stock_quantity__lte=F("reorder_level")).count()
    recent_sales = Sale.objects.select_related("staff").order_by("-created_at")[:6]

    context = {
        "today_revenue": today_revenue,
        "today_orders": today_orders,
        "total_products": total_products,
        "low_stock": low_stock,
        "recent_sales": recent_sales,
    }
    return render(request, "mobile/home.html", context)


@login_required
@admin_required
def mobile_products(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True).select_related("category")
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__icontains=q)
        )
    return render(request, "mobile/products.html", {
        "products": products[:50],
        "q": q,
    })


@login_required
@admin_required
def mobile_suppliers(request):
    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, "mobile/suppliers.html", {"suppliers": suppliers})


@login_required
@admin_required
def mobile_staff(request):
    staff = StaffProfile.objects.select_related("user").filter(is_active=True)
    return render(request, "mobile/staff.html", {"staff_list": staff})


@login_required
@admin_required
def mobile_returns(request):
    returns = Return.objects.select_related("sale", "product").order_by("-created_at")[:30]
    return render(request, "mobile/returns.html", {"returns": returns})


@login_required
@admin_required
def mobile_transactions(request):
    sales = Sale.objects.select_related("staff").order_by("-created_at")[:40]
    return render(request, "mobile/transactions.html", {"sales": sales})


@login_required
@admin_required
def mobile_ledger(request):
    entries = LedgerEntry.objects.order_by("-created_at")[:40]
    return render(request, "mobile/ledger.html", {"entries": entries})


@login_required
@admin_required
def mobile_reports(request):
    return render(request, "mobile/reports.html")