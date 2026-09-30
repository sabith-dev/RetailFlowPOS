from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import admin_required
from .models import Product, Category
from .forms import ProductForm, CategoryForm


@login_required
@admin_required
def product_list(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category", "supplier").all()

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(barcode__icontains=q) |
            Q(brand__icontains=q)
        )

    context = {
        "products": products,
        "q": q,
        "total": products.count(),
    }
    return render(request, "products/list.html", context)


@login_required
@admin_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect("products:list")
    else:
        form = ProductForm()
    return render(request, "products/form.html", {
        "form": form,
        "title": "Add Product",
    })


@login_required
@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect("products:list")
    else:
        form = ProductForm(instance=product)
    return render(request, "products/form.html", {
        "form": form,
        "title": "Edit Product",
        "product": product,
    })


@login_required
@admin_required
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category", "supplier"), pk=pk)
    return render(request, "products/detail.html", {"product": product})


@login_required
@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.is_active = False
        product.save()
        messages.success(request, f"Product '{product.name}' deactivated.")
        return redirect("products:list")
    return render(request, "products/delete_confirm.html", {"product": product})