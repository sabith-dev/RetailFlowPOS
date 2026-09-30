from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from .decorators import admin_required
from .forms import StaffCreateForm, StaffUpdateForm
from .models import StaffProfile


@login_required
@admin_required
def staff_list(request):
    q = request.GET.get("q", "").strip()
    staff = StaffProfile.objects.select_related("user").all()

    if q:
        staff = staff.filter(
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(employee_id__icontains=q) |
            Q(phone__icontains=q)
        )

    context = {
        "staff_list": staff,
        "q": q,
        "total": staff.count(),
    }
    return render(request, "staff/list.html", context)


@login_required
@admin_required
def staff_create(request):
    if request.method == "POST":
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member created successfully.")
            return redirect("accounts:staff_list")
    else:
        form = StaffCreateForm()
    return render(request, "staff/form.html", {
        "form": form,
        "title": "Add Staff",
    })


@login_required
@admin_required
def staff_edit(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    user = profile.user

    if request.method == "POST":
        form = StaffUpdateForm(request.POST, instance=user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member updated successfully.")
            return redirect("accounts:staff_list")
    else:
        form = StaffUpdateForm(instance=user, profile=profile)

    return render(request, "staff/form.html", {
        "form": form,
        "title": "Edit Staff",
        "profile": profile,
    })


@login_required
@admin_required
def staff_detail(request, pk):
    profile = get_object_or_404(StaffProfile.objects.select_related("user"), pk=pk)
    return render(request, "staff/detail.html", {"profile": profile})


@login_required
@admin_required
def staff_deactivate(request, pk):
    profile = get_object_or_404(StaffProfile, pk=pk)
    if request.method == "POST":
        profile.is_active = False
        profile.save()
        profile.user.is_active = False
        profile.user.save()
        messages.success(request, f"Staff '{profile.user.get_full_name() or profile.user.username}' deactivated.")
        return redirect("accounts:staff_list")
    return render(request, "staff/deactivate_confirm.html", {"profile": profile})

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        profile = getattr(user, "profile", None)
        if user.is_superuser or (profile and profile.is_admin):
            return reverse_lazy("dashboard:home")
        return reverse_lazy("billing:pos")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "auth/profile.html", {
        "profile": getattr(request.user, "profile", None)
    })