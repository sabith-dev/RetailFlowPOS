from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name", "company_name", "phone", "email",
            "address", "gst_number", "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "gst_number": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }