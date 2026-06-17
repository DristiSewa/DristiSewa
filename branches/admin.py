from django.contrib import admin

from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = [
        "name", "code", "address", "phone", "email",
        "manager_count", "frontdesk_count", "student_count",
        "is_active", "created_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "code", "address", "email", "phone"]
    list_editable = ["is_active"]
    date_hierarchy = "created_at"
    list_per_page = 50
    ordering = ["name"]

    @admin.display(description="Managers")
    def manager_count(self, obj):
        return obj.staff.filter(role="MANAGER").count()

    @admin.display(description="Front Desk")
    def frontdesk_count(self, obj):
        return obj.staff.filter(role="FRONTDESK").count()

    @admin.display(description="Students")
    def student_count(self, obj):
        return obj.staff.filter(role="STUDENT").count()
