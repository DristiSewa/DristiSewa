from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["student", "doc_type", "status", "remarks", "created_at", "updated_at"]
    list_filter = ["doc_type", "status", "created_at"]
    search_fields = [
        "student__user__email", "student__user__first_name", "student__user__last_name",
        "remarks",
    ]
    list_select_related = ["student", "student__user"]
    list_editable = ["status"]
    date_hierarchy = "created_at"
    list_per_page = 50
