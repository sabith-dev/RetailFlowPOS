from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        profile = getattr(request.user, "profile", None)
        if request.user.is_superuser or (profile and profile.is_admin):
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to access the Admin Portal.")
        return redirect("billing:pos")
    return _wrapped


def staff_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)
    return _wrapped