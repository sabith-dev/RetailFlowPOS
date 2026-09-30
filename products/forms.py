from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "sku", "barcode", "category", "brand", "size", "color",
            "purchase_price", "selling_price", "stock_quantity", "reorder_level",
            "supplier", "image", "description", "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "barcode": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "size": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "purchase_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "selling_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock_quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "reorder_level": forms.NumberInput(attrs={"class": "form-control"}),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }