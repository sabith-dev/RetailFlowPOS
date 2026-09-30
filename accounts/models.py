from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class StaffProfile(models.Model):
    ROLE_ADMIN = "ADMIN"
    ROLE_STAFF = "STAFF"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_STAFF, "Staff"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_STAFF)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    @property
    def is_staff_member(self):
        return self.role == self.ROLE_STAFF


@receiver(post_save, sender=User)
def create_or_update_staff_profile(sender, instance, created, **kwargs):
    if created:
        StaffProfile.objects.get_or_create(user=instance)
    else:
        StaffProfile.objects.get_or_create(user=instance)