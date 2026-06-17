from django.contrib import admin

from .models import Appointment, FollowUp


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ["student", "assigned_to", "note", "scheduled_date", "is_done", "created_at"]
    list_filter = ["is_done", "scheduled_date"]
    search_fields = [
        "student__user__email", "student__user__first_name", "student__user__last_name", "note",
    ]
    list_select_related = ["student", "student__user", "assigned_to"]
    list_editable = ["is_done"]
    date_hierarchy = "scheduled_date"
    list_per_page = 50


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "student", "staff", "purpose", "appointment_date", "appointment_time",
        "status", "created_at",
    ]
    list_filter = ["status", "appointment_date"]
    search_fields = [
        "student__user__email", "student__user__first_name", "student__user__last_name", "purpose",
    ]
    list_select_related = ["student", "student__user", "staff"]
    list_editable = ["status"]
    date_hierarchy = "appointment_date"
    list_per_page = 50
