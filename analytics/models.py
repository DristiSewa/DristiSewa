from django.conf import settings
from django.db import models
from django.utils import timezone


class DetailedActivityLog(models.Model):
    """Enhanced audit trail capturing all system actions across all branches.

    Superadmin sees complete action history with IP addresses, user agents, and impact metrics.
    """

    class Action(models.TextChoices):
        LOGIN = "LOGIN", "User Login"
        LOGOUT = "LOGOUT", "User Logout"
        USER_CREATE = "USER_CREATE", "User Created"
        USER_UPDATE = "USER_UPDATE", "User Updated"
        USER_DELETE = "USER_DELETE", "User Deleted"
        STUDENT_CREATE = "STUDENT_CREATE", "Student Created"
        STUDENT_UPDATE = "STUDENT_UPDATE", "Student Updated"
        STUDENT_VERIFY = "STUDENT_VERIFY", "Student Verified"
        DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD", "Document Uploaded"
        DOCUMENT_APPROVE = "DOCUMENT_APPROVE", "Document Approved"
        DOCUMENT_REJECT = "DOCUMENT_REJECT", "Document Rejected"
        DOCUMENT_DELETE = "DOCUMENT_DELETE", "Document Deleted"
        APPLICATION_CREATE = "APPLICATION_CREATE", "Application Created"
        APPLICATION_UPDATE = "APPLICATION_UPDATE", "Application Status Updated"
        FOLLOWUP_CREATE = "FOLLOWUP_CREATE", "Follow-up Created"
        FOLLOWUP_COMPLETE = "FOLLOWUP_COMPLETE", "Follow-up Completed"
        BRANCH_CREATE = "BRANCH_CREATE", "Branch Created"
        BRANCH_UPDATE = "BRANCH_UPDATE", "Branch Updated"
        BRANCH_DEACTIVATE = "BRANCH_DEACTIVATE", "Branch Deactivated"
        STAFF_ASSIGN = "STAFF_ASSIGN", "Staff Assigned"
        PERMISSION_CHANGE = "PERMISSION_CHANGE", "User Permission Changed"
        SYSTEM_ERROR = "SYSTEM_ERROR", "System Error"
        DATA_EXPORT = "DATA_EXPORT", "Data Exported"
        BULK_ACTION = "BULK_ACTION", "Bulk Action Performed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detailed_activity_logs"
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs"
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    description = models.TextField(blank=True)
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("SUCCESS", "Success"), ("FAILED", "Failed"), ("PENDING", "Pending")],
        default="SUCCESS"
    )
    changes = models.JSONField(null=True, blank=True, help_text="What changed (before/after)")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["branch", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} by {self.user} ({self.created_at:%Y-%m-%d %H:%M})"


class AggregatedAnalytics(models.Model):
    """Pre-calculated metrics aggregated daily for fast admin dashboard access.

    Stores daily snapshots of key metrics to enable quick access without recalculating
    from millions of transaction records.
    """

    date = models.DateField(db_index=True)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="daily_analytics"
    )

    # Student metrics
    total_students = models.IntegerField(default=0)
    new_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    verified_students = models.IntegerField(default=0)
    archived_students = models.IntegerField(default=0)

    # Application metrics
    total_applications = models.IntegerField(default=0)
    applications_pending = models.IntegerField(default=0)
    applications_approved = models.IntegerField(default=0)
    applications_rejected = models.IntegerField(default=0)
    applications_visa_granted = models.IntegerField(default=0)

    # Document metrics
    total_documents = models.IntegerField(default=0)
    documents_pending = models.IntegerField(default=0)
    documents_approved = models.IntegerField(default=0)
    documents_rejected = models.IntegerField(default=0)

    # Follow-up metrics
    followups_pending = models.IntegerField(default=0)
    followups_completed = models.IntegerField(default=0)

    # Staff metrics
    total_managers = models.IntegerField(default=0)
    total_frontdesk = models.IntegerField(default=0)

    # Performance metrics
    visa_success_rate = models.FloatField(default=0.0)
    student_growth_percentage = models.FloatField(default=0.0)
    avg_documents_per_student = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("date", "branch")
        indexes = [
            models.Index(fields=["date", "branch"]),
            models.Index(fields=["-date"]),
        ]

    def __str__(self):
        return f"{self.branch.name} - {self.date}"


class SystemHealthMetrics(models.Model):
    """System performance and health metrics.

    Tracks database performance, API response times, error rates, and system capacity.
    """

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Database metrics
    database_size_mb = models.FloatField(null=True, blank=True)
    active_connections = models.IntegerField(default=0)
    query_time_ms = models.FloatField(default=0.0)

    # Application metrics
    request_count_hourly = models.IntegerField(default=0)
    avg_response_time_ms = models.FloatField(default=0.0)
    error_count_hourly = models.IntegerField(default=0)

    # System metrics
    cpu_usage_percent = models.FloatField(default=0.0)
    memory_usage_percent = models.FloatField(default=0.0)
    disk_usage_percent = models.FloatField(default=0.0)

    # Cache metrics
    cache_hit_rate = models.FloatField(default=0.0)

    status = models.CharField(
        max_length=20,
        choices=[
            ("HEALTHY", "Healthy"),
            ("DEGRADED", "Degraded"),
            ("CRITICAL", "Critical")
        ],
        default="HEALTHY"
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
        ]

    def __str__(self):
        return f"{self.get_status_display()} - {self.timestamp:%Y-%m-%d %H:%M}"


class BranchPerformanceSnapshot(models.Model):
    """Monthly branch performance snapshot for comparison and trend analysis."""

    month = models.DateField()  # First day of month
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="performance_snapshots"
    )

    # Enrollment metrics
    total_students_month_end = models.IntegerField(default=0)
    new_enrollments = models.IntegerField(default=0)

    # Outcomes
    applications_submitted = models.IntegerField(default=0)
    visas_granted = models.IntegerField(default=0)
    visa_success_rate = models.FloatField(default=0.0)

    # Efficiency
    avg_days_to_visa = models.IntegerField(default=0)
    document_approval_rate = models.FloatField(default=0.0)

    # Staff performance
    avg_students_per_staff = models.FloatField(default=0.0)
    staff_satisfaction_score = models.FloatField(null=True, blank=True)

    # Rankings (computed)
    rank_among_branches = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-month"]
        unique_together = ("month", "branch")
        indexes = [
            models.Index(fields=["month", "branch"]),
            models.Index(fields=["-month"]),
        ]

    def __str__(self):
        return f"{self.branch.name} - {self.month:%B %Y}"


class UserEngagementMetrics(models.Model):
    """Track user engagement patterns for each role."""

    date = models.DateField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="engagement_metrics"
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Engagement
    login_count = models.IntegerField(default=0)
    active_sessions = models.IntegerField(default=0)
    total_actions = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    # Work done
    students_processed = models.IntegerField(default=0)
    documents_reviewed = models.IntegerField(default=0)
    followups_completed = models.IntegerField(default=0)

    # Quality
    average_response_time_hours = models.FloatField(default=0.0)
    error_rate = models.FloatField(default=0.0)

    class Meta:
        ordering = ["-date"]
        unique_together = ("date", "user")
        indexes = [
            models.Index(fields=["user", "-date"]),
            models.Index(fields=["branch", "-date"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.date}"
