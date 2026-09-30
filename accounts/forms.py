from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import StaffProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Username",
            "autofocus": True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Password",
        })
    )


class StaffCreateForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    role = forms.ChoiceField(
        choices=StaffProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    employee_id = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
            profile = user.profile
            profile.phone = self.cleaned_data.get("phone", "")
            profile.role = self.cleaned_data["role"]
            profile.employee_id = self.cleaned_data.get("employee_id") or None
            profile.address = self.cleaned_data.get("address", "")
            profile.save()
        return user


class StaffUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    role = forms.ChoiceField(
        choices=StaffProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    employee_id = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)
        if self.profile:
            self.fields["phone"].initial = self.profile.phone
            self.fields["role"].initial = self.profile.role
            self.fields["employee_id"].initial = self.profile.employee_id
            self.fields["address"].initial = self.profile.address
            self.fields["is_active"].initial = self.profile.is_active

    def save(self, commit=True):
        user = super().save(commit=commit)
        if self.profile:
            self.profile.phone = self.cleaned_data.get("phone", "")
            self.profile.role = self.cleaned_data["role"]
            self.profile.employee_id = self.cleaned_data.get("employee_id") or None
            self.profile.address = self.cleaned_data.get("address", "")
            self.profile.is_active = self.cleaned_data.get("is_active", True)
            self.profile.save()
            # Keep Django's is_active in sync
            user.is_active = self.profile.is_active
            user.save()
        return user