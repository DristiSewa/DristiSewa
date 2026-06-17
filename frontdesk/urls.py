from django.urls import path

from . import views

app_name = "frontdesk"

urlpatterns = [
    path("students/", views.student_list, name="student_list"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("students/<int:pk>/edit/", views.student_edit, name="student_edit"),
    path("students/<int:pk>/update-status/", views.student_status_update, name="student_status_update"),
]
