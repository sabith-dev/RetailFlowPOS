from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StaffProfile


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = "Profile"


class UserAdmin(BaseUserAdmin):
    inlines = [StaffProfileInline]
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "get_role")
    list_filter = ("is_staff", "is_superuser", "is_active")

    def get_role(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.role
        return "-"
    get_role.short_description = "Role"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "employee_id", "phone", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "user__first_name", "employee_id", "phone")