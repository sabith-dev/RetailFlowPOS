from django.db import models   
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from accounts.decorators import admin_required
from billing.models import Sale, SaleItem
from products.models import Product
from ledger.models import LedgerEntry
from .models import Return
from .forms import ReturnForm


@login_required
@admin_required
def return_list(request):
    q = request.GET.get("q", "").strip()
    returns = Return.objects.select_related(
        "sale", "product", "processed_by"
    ).order_by("-created_at")

    if q:
        returns = returns.filter(
            Q(sale__invoice_number__icontains=q) |
            Q(product__name__icontains=q) |
            Q(reason__icontains=q)
        )

    context = {
        "returns": returns,
        "q": q,
        "total": returns.count(),
    }
    return render(request, "returns/list.html", context)


@login_required
@admin_required
def return_create(request):
    if request.method == "POST":
        form = ReturnForm(request.POST)
        if form.is_valid():
            sale = form.cleaned_data["sale"]
            sale_item = form.cleaned_data["sale_item"]
            quantity = form.cleaned_data["quantity"]
            reason = form.cleaned_data["reason"]
            notes = form.cleaned_data.get("notes", "")

            # Validations
            if sale_item.sale_id != sale.id:
                messages.error(request, "Selected product does not belong to this invoice.")
                return redirect("returns:create")

            if quantity > sale_item.quantity:
                messages.error(request, f"Cannot return more than purchased quantity ({sale_item.quantity}).")
                return redirect("returns:create")

            # Check already returned quantity for this item
            already_returned = Return.objects.filter(
                sale_item=sale_item, status=Return.STATUS_APPROVED
            ).aggregate(total=models.Sum("quantity"))["total"] or 0

            if already_returned + quantity > sale_item.quantity:
                messages.error(
                    request,
                    f"Already returned {already_returned}. Max remaining: {sale_item.quantity - already_returned}"
                )
                return redirect("returns:create")

            refund_amount = (sale_item.unit_price * quantity)

            try:
                with transaction.atomic():
                    # Create Return
                    ret = Return.objects.create(
                        sale=sale,
                        product=sale_item.product,
                        sale_item=sale_item,
                        quantity=quantity,
                        reason=reason,
                        refund_amount=refund_amount,
                        processed_by=request.user,
                        status=Return.STATUS_APPROVED,
                        notes=notes,
                    )

                    # Increase stock
                    product = Product.objects.select_for_update().get(pk=sale_item.product_id)
                    product.stock_quantity += quantity
                    product.save(update_fields=["stock_quantity"])

                    # Ledger entry (debit)
                    last = LedgerEntry.objects.order_by("-created_at").first()
                    balance = (last.balance if last else Decimal("0")) - refund_amount

                    LedgerEntry.objects.create(
                        entry_type=LedgerEntry.TYPE_RETURN,
                        reference=sale.invoice_number,
                        description=f"Return #{ret.id} - {product.name} x{quantity}",
                        debit=refund_amount,
                        credit=Decimal("0.00"),
                        balance=balance,
                    )

                messages.success(
                    request,
                    f"Return processed. Refund: ₹{refund_amount}. Stock updated."
                )
                return redirect("returns:list")

            except Exception as e:
                messages.error(request, f"Error processing return: {e}")
                return redirect("returns:create")
    else:
        form = ReturnForm()

    return render(request, "returns/form.html", {
        "form": form,
        "title": "Process Return",
    })


@login_required
@admin_required
def return_detail(request, pk):
    ret = get_object_or_404(
        Return.objects.select_related("sale", "product", "processed_by", "sale_item"),
        pk=pk
    )
    return render(request, "returns/detail.html", {"ret": ret})