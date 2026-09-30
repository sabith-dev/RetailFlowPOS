from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product


class Sale(models.Model):
    PAYMENT_CASH = "CASH"
    PAYMENT_UPI = "UPI"
    PAYMENT_CARD = "CARD"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_UPI, "UPI"),
        (PAYMENT_CARD, "Card"),
    ]

    STATUS_COMPLETED = "COMPLETED"
    STATUS_PENDING = "PENDING"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (STATUS_COMPLETED, "Completed"),
        (STATUS_PENDING, "Pending"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, editable=False)
    customer_name = models.CharField(max_length=200, blank=True, default="Walk-in Customer")
    customer_phone = models.CharField(max_length=20, blank=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sales")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    payment_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_COMPLETED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            today = timezone.now().strftime("%Y%m%d")
            last = Sale.objects.filter(invoice_number__startswith=f"INV-{today}").count()
            self.invoice_number = f"INV-{today}-{last + 1:04d}"
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)


class Payment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=Sale.PAYMENT_CHOICES)
    transaction_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return f"{self.method} - {self.amount} for {self.sale.invoice_number}"