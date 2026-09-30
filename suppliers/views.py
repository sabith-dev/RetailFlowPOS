from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import admin_required
from .models import Supplier
from .forms import SupplierForm


@login_required
@admin_required
def supplier_list(request):
    q = request.GET.get("q", "").strip()
    suppliers = Supplier.objects.all()

    if q:
        suppliers = suppliers.filter(
            Q(name__icontains=q) |
            Q(company_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(gst_number__icontains=q)
        )

    context = {
        "suppliers": suppliers,
        "q": q,
        "total": suppliers.count(),
    }
    return render(request, "suppliers/list.html", context)


@login_required
@admin_required
def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier created successfully.")
            return redirect("suppliers:list")
    else:
        form = SupplierForm()
    return render(request, "suppliers/form.html", {
        "form": form,
        "title": "Add Supplier",
    })


@login_required
@admin_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect("suppliers:list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "suppliers/form.html", {
        "form": form,
        "title": "Edit Supplier",
        "supplier": supplier,
    })


@login_required
@admin_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    products = supplier.products.filter(is_active=True)
    return render(request, "suppliers/detail.html", {
        "supplier": supplier,
        "products": products,
    })


@login_required
@admin_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.is_active = False
        supplier.save()
        messages.success(request, f"Supplier '{supplier.name}' deactivated.")
        return redirect("suppliers:list")
    return render(request, "suppliers/delete_confirm.html", {"supplier": supplier})