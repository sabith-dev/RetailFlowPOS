from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_home, name="home"),
    path("sales/", views.sales_report, name="sales"),
    path("inventory/", views.inventory_report, name="inventory"),
    path("profit/", views.profit_report, name="profit"),
]