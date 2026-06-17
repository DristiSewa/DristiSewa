from django.urls import path

from . import views

app_name = "followups"

urlpatterns = [
    path("", views.followup_list, name="followup_list"),
    path("<int:pk>/toggle/", views.followup_toggle, name="followup_toggle"),
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/<int:pk>/edit/", views.appointment_update, name="appointment_update"),
    path("appointments/<int:pk>/cancel/", views.appointment_cancel, name="appointment_cancel"),
]
