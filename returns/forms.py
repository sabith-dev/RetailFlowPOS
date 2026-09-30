from django import forms
from .models import Return
from billing.models import Sale, SaleItem


class ReturnForm(forms.Form):
    sale = forms.ModelChoiceField(
        queryset=Sale.objects.filter(payment_status="COMPLETED").order_by("-created_at"),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Invoice / Sale"
    )
    sale_item = forms.ModelChoiceField(
        queryset=SaleItem.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Product from Invoice"
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1})
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        required=True
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "sale" in self.data:
            try:
                sale_id = int(self.data.get("sale"))
                self.fields["sale_item"].queryset = SaleItem.objects.filter(sale_id=sale_id).select_related("product")
            except (ValueError, TypeError):
                self.fields["sale_item"].queryset = SaleItem.objects.none()
        elif self.initial.get("sale"):
            self.fields["sale_item"].queryset = SaleItem.objects.filter(
                sale=self.initial["sale"]
            ).select_related("product")