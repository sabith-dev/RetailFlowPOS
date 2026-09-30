from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from billing.models import Sale, SaleItem
from products.models import Product


class Return(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="returns")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="returns")
    sale_item = models.ForeignKey(SaleItem, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    reason = models.TextField()
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="processed_returns")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Return #{self.id} - {self.product.name} x{self.quantity}"