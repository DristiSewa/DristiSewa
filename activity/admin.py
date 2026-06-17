from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "description", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "description"]
    readonly_fields = ["user", "action", "description", "created_at"]
    list_select_related = ["user"]
    date_hierarchy = "created_at"
    list_per_page = 50
    ordering = ["-created_at"]
