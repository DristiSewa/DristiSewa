from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("management/", views.student_management, name="student_management"),
    path("management/add/", views.student_create, name="student_create"),
    path("management/<int:pk>/edit/", views.student_edit, name="student_edit"),
    path("management/<int:pk>/profile/", views.student_profile_view, name="student_profile"),
    path("management/<int:pk>/archive/", views.student_archive, name="student_archive"),
    path("management/<int:pk>/verify/", views.student_verify, name="student_verify"),
    path("archived/", views.archived_students, name="archived_students"),
    path("archived/<int:pk>/unarchive/", views.student_unarchive, name="student_unarchive"),
]
