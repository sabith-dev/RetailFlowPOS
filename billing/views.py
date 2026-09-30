from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from accounts.decorators import staff_required
from products.models import Product
from .models import Sale, SaleItem, Payment
from ledger.models import LedgerEntry


def _get_cart(request):
    return request.session.get("cart", {})


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


@login_required
@staff_required
def pos(request):
    """Main POS screen."""
    q = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0)

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(barcode__icontains=q) |
            Q(brand__icontains=q)
        )[:30]
    else:
        products = products.order_by("name")[:20]

    cart = _get_cart(request)
    cart_items = []
    subtotal = Decimal("0.00")

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
            qty = int(item["quantity"])
            line_total = product.selling_price * qty
            cart_items.append({
                "product": product,
                "quantity": qty,
                "unit_price": product.selling_price,
                "total": line_total,
            })
            subtotal += line_total
        except Product.DoesNotExist:
            continue

    discount = Decimal(request.session.get("cart_discount", "0"))
    grand_total = max(subtotal - discount, Decimal("0.00"))

    context = {
        "products": products,
        "q": q,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount": discount,
        "grand_total": grand_total,
        "cart_count": sum(i["quantity"] for i in cart_items),
    }
    return render(request, "billing/pos.html", context)


@login_required
@staff_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request)

    pid = str(product_id)
    if pid in cart:
        new_qty = cart[pid]["quantity"] + 1
    else:
        new_qty = 1

    if new_qty > product.stock_quantity:
        messages.error(request, f"Only {product.stock_quantity} units available for {product.name}.")
        return redirect("billing:pos")

    cart[pid] = {
        "quantity": new_qty,
        "name": product.name,
        "price": str(product.selling_price),
    }
    _save_cart(request, cart)
    messages.success(request, f"Added {product.name}")
    return redirect("billing:pos")


@login_required
@staff_required
def cart_update(request, product_id):
    if request.method != "POST":
        return redirect("billing:pos")

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request)
    pid = str(product_id)

    try:
        qty = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        qty = 1

    if qty <= 0:
        if pid in cart:
            del cart[pid]
        _save_cart(request, cart)
        return redirect("billing:pos")

    if qty > product.stock_quantity:
        messages.error(request, f"Only {product.stock_quantity} units available.")
        return redirect("billing:pos")

    cart[pid] = {
        "quantity": qty,
        "name": product.name,
        "price": str(product.selling_price),
    }
    _save_cart(request, cart)
    return redirect("billing:pos")


@login_required
@staff_required
def cart_remove(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        _save_cart(request, cart)
    return redirect("billing:pos")


@login_required
@staff_required
def cart_clear(request):
    request.session["cart"] = {}
    request.session["cart_discount"] = "0"
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    return redirect("billing:pos")


@login_required
@staff_required
def apply_discount(request):
    if request.method == "POST":
        try:
            discount = Decimal(request.POST.get("discount", "0"))
            if discount < 0:
                discount = Decimal("0")
        except:
            discount = Decimal("0")
        request.session["cart_discount"] = str(discount)
        request.session.modified = True
    return redirect("billing:pos")


@login_required
@staff_required
@transaction.atomic
def checkout(request):
    """Process payment and create Sale + reduce stock + ledger entry."""
    if request.method != "POST":
        return redirect("billing:pos")

    cart = _get_cart(request)
    if not cart:
        messages.error(request, "Cart is empty.")
        return redirect("billing:pos")

    customer_name = request.POST.get("customer_name", "Walk-in Customer").strip() or "Walk-in Customer"
    customer_phone = request.POST.get("customer_phone", "").strip()
    payment_method = request.POST.get("payment_method", "CASH")
    transaction_ref = request.POST.get("transaction_reference", "").strip()

    if payment_method not in ("CASH", "UPI", "CARD"):
        payment_method = "CASH"

    # Build cart items & validate stock
    items = []
    subtotal = Decimal("0.00")

    for product_id, data in cart.items():
        product = Product.objects.select_for_update().get(pk=product_id, is_active=True)
        qty = int(data["quantity"])
        if qty > product.stock_quantity:
            messages.error(request, f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")
            return redirect("billing:pos")
        line_total = product.selling_price * qty
        items.append({
            "product": product,
            "quantity": qty,
            "unit_price": product.selling_price,
            "total": line_total,
        })
        subtotal += line_total

    discount = Decimal(request.session.get("cart_discount", "0"))
    grand_total = max(subtotal - discount, Decimal("0.00"))

    # Create Sale
    sale = Sale.objects.create(
        customer_name=customer_name,
        customer_phone=customer_phone,
        staff=request.user,
        subtotal=subtotal,
        discount=discount,
        tax=Decimal("0.00"),
        grand_total=grand_total,
        payment_method=payment_method,
        payment_status=Sale.STATUS_COMPLETED,
    )

    # Create SaleItems + reduce stock
    for item in items:
        SaleItem.objects.create(
            sale=sale,
            product=item["product"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            discount=Decimal("0.00"),
            total=item["total"],
        )
        # Reduce stock
        product = item["product"]
        product.stock_quantity -= item["quantity"]
        product.save(update_fields=["stock_quantity"])

    # Create Payment
    Payment.objects.create(
        sale=sale,
        amount=grand_total,
        method=payment_method,
        transaction_reference=transaction_ref,
    )

    # Ledger entry
    last_balance = LedgerEntry.objects.order_by("-created_at").first()
    balance = (last_balance.balance if last_balance else Decimal("0")) + grand_total

    LedgerEntry.objects.create(
        entry_type=LedgerEntry.TYPE_SALE,
        reference=sale.invoice_number,
        description=f"Sale {sale.invoice_number} - {customer_name}",
        debit=Decimal("0.00"),
        credit=grand_total,
        balance=balance,
    )

    # Clear cart
    request.session["cart"] = {}
    request.session["cart_discount"] = "0"
    request.session.modified = True

    messages.success(request, f"Sale completed! Invoice: {sale.invoice_number}")
    return redirect("billing:invoice", invoice_number=sale.invoice_number)


@login_required
@staff_required
def invoice(request, invoice_number):
    sale = get_object_or_404(
        Sale.objects.select_related("staff").prefetch_related("items__product", "payments"),
        invoice_number=invoice_number
    )
    return render(request, "billing/invoice.html", {"sale": sale})


@login_required
@staff_required
def transactions(request):
    sales = Sale.objects.select_related("staff").order_by("-created_at")[:100]
    return render(request, "billing/transactions.html", {"sales": sales})