from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    # Staff Management
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/create/", views.staff_create, name="staff_create"),
    path("staff/<int:pk>/", views.staff_detail, name="staff_detail"),
    path("staff/<int:pk>/edit/", views.staff_edit, name="staff_edit"),
    path("staff/<int:pk>/deactivate/", views.staff_deactivate, name="staff_deactivate"),
]