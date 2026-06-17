from django.contrib import admin
from django.utils.html import format_html

from .models import (
    DetailedActivityLog,
    AggregatedAnalytics,
    SystemHealthMetrics,
    BranchPerformanceSnapshot,
    UserEngagementMetrics,
)


@admin.register(DetailedActivityLog)
class DetailedActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'action_colored',
        'entity_type',
        'branch',
        'status_colored',
        'created_at'
    ]
    list_filter = ['action', 'status', 'branch', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'description', 'entity_id']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']

    def action_colored(self, obj):
        colors = {
            'LOGIN': '#28a745',
            'LOGOUT': '#dc3545',
            'USER_CREATE': '#17a2b8',
            'USER_DELETE': '#dc3545',
            'STUDENT_CREATE': '#28a745',
            'STUDENT_UPDATE': '#ffc107',
            'DOCUMENT_APPROVE': '#28a745',
            'DOCUMENT_REJECT': '#dc3545',
            'APPLICATION_UPDATE': '#ffc107',
            'SYSTEM_ERROR': '#dc3545',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_colored.short_description = 'Action'

    def status_colored(self, obj):
        colors = {
            'SUCCESS': '#28a745',
            'FAILED': '#dc3545',
            'PENDING': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(AggregatedAnalytics)
class AggregatedAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'branch',
        'date',
        'total_students',
        'total_applications',
        'visa_success_rate',
        'total_documents'
    ]
    list_filter = ['branch', 'date']
    readonly_fields = ['updated_at']

    fieldsets = (
        ('Date & Branch', {
            'fields': ('date', 'branch')
        }),
        ('Student Metrics', {
            'fields': (
                'total_students',
                'new_students',
                'active_students',
                'verified_students',
                'archived_students'
            )
        }),
        ('Application Metrics', {
            'fields': (
                'total_applications',
                'applications_pending',
                'applications_approved',
                'applications_rejected',
                'applications_visa_granted'
            )
        }),
        ('Document Metrics', {
            'fields': (
                'total_documents',
                'documents_pending',
                'documents_approved',
                'documents_rejected'
            )
        }),
        ('Follow-up Metrics', {
            'fields': (
                'followups_pending',
                'followups_completed'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'visa_success_rate',
                'student_growth_percentage',
                'avg_documents_per_student'
            )
        }),
        ('Metadata', {
            'fields': ('updated_at',)
        }),
    )


@admin.register(SystemHealthMetrics)
class SystemHealthMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'status_colored',
        'database_size_mb',
        'query_time_ms',
        'error_count_hourly'
    ]
    list_filter = ['status', 'timestamp']
    readonly_fields = ['timestamp']

    def status_colored(self, obj):
        colors = {
            'HEALTHY': '#28a745',
            'DEGRADED': '#ffc107',
            'CRITICAL': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'


@admin.register(BranchPerformanceSnapshot)
class BranchPerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'branch',
        'month',
        'total_students_month_end',
        'visa_success_rate',
        'rank_among_branches'
    ]
    list_filter = ['branch', 'month']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserEngagementMetrics)
class UserEngagementMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'branch',
        'date',
        'login_count',
        'total_actions',
        'students_processed'
    ]
    list_filter = ['date', 'branch', 'user__role']
    search_fields = ['user__email', 'user__first_name']
    readonly_fields = []
