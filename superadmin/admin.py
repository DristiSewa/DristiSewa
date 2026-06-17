from django.contrib import admin
from django.utils.html import format_html

from .models import SuperAdmin, DatabaseBackup, DataExport, DataImport, SuperAdminAuditLog, DatabaseStatistics


@admin.register(SuperAdmin)
class SuperAdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active_badge', 'login_count', 'last_login', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active', 'created_at', 'updated_at')
        }),
        ('Access Permissions', {
            'fields': (
                'can_manage_users',
                'can_manage_branches',
                'can_manage_students',
                'can_manage_applications',
                'can_manage_documents',
                'can_view_analytics',
            )
        }),
        ('System Permissions', {
            'fields': (
                'can_export_data',
                'can_import_data',
                'can_backup_database',
                'can_restore_database',
                'can_manage_system',
                'can_view_audit_logs',
            )
        }),
        ('Login Tracking', {
            'fields': ('last_login', 'login_count'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def is_active_badge(self, obj):
        color = '#28a745' if obj.is_active else '#dc3545'
        status = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    is_active_badge.short_description = 'Status'


@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'backup_type', 'file_size_mb', 'record_count', 'is_verified_badge']
    list_filter = ['backup_type', 'is_verified', 'created_at']
    search_fields = ['description']
    readonly_fields = ['created_at']

    def is_verified_badge(self, obj):
        color = '#28a745' if obj.is_verified else '#ffc107'
        status = 'Verified' if obj.is_verified else 'Unverified'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    is_verified_badge.short_description = 'Verified'


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'export_type', 'record_count', 'file_size_mb', 'created_by']
    list_filter = ['export_type', 'created_at']
    search_fields = ['description', 'tables_included']
    readonly_fields = ['created_at']


@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'import_type', 'status_badge', 'successful_records', 'failed_records', 'created_by']
    list_filter = ['import_type', 'status', 'created_at']
    search_fields = ['error_details']
    readonly_fields = ['created_at', 'completed_at']

    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffc107',
            'PROCESSING': '#17a2b8',
            'COMPLETED': '#28a745',
            'FAILED': '#dc3545',
            'PARTIAL': '#ff9800',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(SuperAdminAuditLog)
class SuperAdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'action_badge', 'superadmin', 'affected_records', 'status_badge']
    list_filter = ['action', 'status', 'created_at']
    search_fields = ['description', 'superadmin__user__email']
    readonly_fields = ['created_at']

    def action_badge(self, obj):
        colors = {
            'LOGIN': '#28a745',
            'LOGOUT': '#dc3545',
            'DATABASE_BACKUP': '#17a2b8',
            'DATA_EXPORT': '#6f42c1',
            'DATA_IMPORT': '#ff9800',
            'BULK_DELETE': '#dc3545',
            'FAILED_ACTION': '#dc3545',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Action'

    def status_badge(self, obj):
        color = '#28a745' if obj.status == 'SUCCESS' else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(DatabaseStatistics)
class DatabaseStatisticsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'total_students', 'total_applications', 'total_documents', 'database_size_mb']
    list_filter = ['timestamp']
    readonly_fields = ['timestamp']

    fieldsets = (
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
        ('User & Branch Data', {
            'fields': ('total_users', 'total_branches')
        }),
        ('Student Data', {
            'fields': (
                'total_students',
                'active_students',
                'archived_students',
                'verified_students'
            )
        }),
        ('Application Data', {
            'fields': (
                'total_applications',
                'pending_applications',
                'approved_applications',
                'rejected_applications',
                'visa_granted_applications'
            )
        }),
        ('Document & Follow-up Data', {
            'fields': (
                'total_documents',
                'pending_documents',
                'approved_documents',
                'pending_followups',
                'completed_followups',
                'total_followups'
            )
        }),
        ('Activity & Health', {
            'fields': (
                'logins_today',
                'actions_today',
                'database_size_mb'
            )
        }),
    )
