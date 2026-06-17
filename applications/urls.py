from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("status/", views.app_status, name="app_status"),
    path("", views.application_list, name="application_list"),
    path("new/", views.application_create, name="application_create"),
    path("<int:pk>/edit/", views.application_update, name="application_update"),
]
