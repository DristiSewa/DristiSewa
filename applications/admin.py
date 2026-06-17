from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "student", "destination_country", "institution", "status",
        "created_at", "updated_at",
    ]
    list_filter = ["status", "destination_country", "created_at"]
    search_fields = [
        "student__user__email", "student__user__first_name", "student__user__last_name",
        "institution",
    ]
    list_select_related = ["student", "student__user"]
    list_editable = ["status"]
    date_hierarchy = "created_at"
    list_per_page = 50
