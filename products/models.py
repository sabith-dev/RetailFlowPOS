from django.db import models
from suppliers.models import Supplier


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    brand = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    @property
    def is_out_of_stock(self):
        return self.stock_quantity == 0