from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("pos/", views.pos, name="pos"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("discount/", views.apply_discount, name="apply_discount"),
    path("checkout/", views.checkout, name="checkout"),
    path("invoice/<str:invoice_number>/", views.invoice, name="invoice"),
    path("transactions/", views.transactions, name="transactions"),
]