from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        "user", "college", "preferred_country", "test_type", "test_score",
        "assigned_to", "date_of_birth", "passed_year", "gpa",
        "is_verified", "is_archived", "created_at",
    ]
    search_fields = [
        "user__email", "user__first_name", "user__last_name", "college",
        "assigned_to__email", "assigned_to__first_name", "assigned_to__last_name",
    ]
    list_filter = ["test_type", "preferred_country", "is_archived", "is_verified", "user__branch"]
    list_select_related = ["user", "assigned_to"]
    list_editable = ["is_verified", "is_archived"]
    date_hierarchy = "created_at"
    list_per_page = 50
