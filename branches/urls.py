from django.urls import path

from . import views

app_name = "branches"

urlpatterns = [
    path("", views.create_branch, name="create_branch"),
    path("staff/", views.branch_staff, name="branch_staff"),
    path("staff/<int:branch_id>/", views.branch_staff, name="branch_staff"),
    path("create-json/", views.create_branch_json, name="create_branch_json"),
    path("update-json/<int:branch_id>/", views.update_branch_json, name="update_branch_json"),
    path("delete-json/<int:branch_id>/", views.delete_branch_json, name="delete_branch_json"),
    path("reactivate/<int:branch_id>/", views.reactivate_branch, name="reactivate_branch"),
]
