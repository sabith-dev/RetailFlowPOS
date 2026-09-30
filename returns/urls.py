from django.urls import path
from . import views

app_name = "returns"

urlpatterns = [
    path("", views.return_list, name="list"),
    path("create/", views.return_create, name="create"),
    path("<int:pk>/", views.return_detail, name="detail"),
]