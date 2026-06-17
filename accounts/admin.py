from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import OTPVerification, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["email"]
    list_display = [
        "email", "first_name", "last_name", "role", "branch",
        "phone", "is_staff", "is_active", "is_superuser",
        "last_login", "date_joined",
    ]
    list_filter = ["role", "branch", "is_staff", "is_active", "is_superuser"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    list_select_related = ["branch"]
    list_per_page = 50
    date_hierarchy = "date_joined"
    list_editable = ["is_active"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "profile_pic")}),
        ("Role & Branch", {"fields": ("role", "branch")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "role", "branch", "password1", "password2"),
            },
        ),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ["email", "otp", "purpose", "is_verified", "created_at"]
    list_filter = ["purpose", "is_verified", "created_at"]
    search_fields = ["email"]
    date_hierarchy = "created_at"
    list_per_page = 50
    ordering = ["-created_at"]
