from django.db import models
from django.utils import timezone


class LedgerEntry(models.Model):
    TYPE_SALE = "SALE"
    TYPE_RETURN = "RETURN"
    TYPE_PURCHASE = "PURCHASE"
    TYPE_EXPENSE = "EXPENSE"
    TYPE_OTHER = "OTHER"
    TYPE_CHOICES = [
        (TYPE_SALE, "Sale"),
        (TYPE_RETURN, "Return"),
        (TYPE_PURCHASE, "Purchase"),
        (TYPE_EXPENSE, "Expense"),
        (TYPE_OTHER, "Other"),
    ]

    entry_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Ledger Entries"

    def __str__(self):
        return f"{self.entry_type} - {self.description} ({self.created_at.date()})"