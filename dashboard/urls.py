from django.urls import path
from . import views
from . import mobile_views

app_name = "dashboard"

urlpatterns = [
    # Desktop
    path("", views.home, name="home"),
    path("dashboard/", views.home, name="dashboard"),

    # Mobile Admin
    path("mobile/", mobile_views.mobile_home, name="mobile_home"),
    path("mobile/products/", mobile_views.mobile_products, name="mobile_products"),
    path("mobile/suppliers/", mobile_views.mobile_suppliers, name="mobile_suppliers"),
    path("mobile/staff/", mobile_views.mobile_staff, name="mobile_staff"),
    path("mobile/returns/", mobile_views.mobile_returns, name="mobile_returns"),
    path("mobile/transactions/", mobile_views.mobile_transactions, name="mobile_transactions"),
    path("mobile/ledger/", mobile_views.mobile_ledger, name="mobile_ledger"),
    path("mobile/reports/", mobile_views.mobile_reports, name="mobile_reports"),
]