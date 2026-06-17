from django.conf import settings
from django.db import models
from django.utils import timezone


class SuperAdmin(models.Model):
    """Enhanced superadmin account with additional permissions and audit features."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='superadmin_profile'
    )

    # Access Control
    can_manage_users = models.BooleanField(default=True, help_text="Can create/edit/delete users")
    can_manage_branches = models.BooleanField(default=True, help_text="Can create/edit/delete branches")
    can_manage_students = models.BooleanField(default=True, help_text="Can manage all students")
    can_manage_applications = models.BooleanField(default=True, help_text="Can manage applications")
    can_manage_documents = models.BooleanField(default=True, help_text="Can manage documents")
    can_view_analytics = models.BooleanField(default=True, help_text="Can view analytics")
    can_export_data = models.BooleanField(default=True, help_text="Can export database records")
    can_import_data = models.BooleanField(default=True, help_text="Can import bulk data")
    can_backup_database = models.BooleanField(default=True, help_text="Can create database backups")
    can_restore_database = models.BooleanField(default=True, help_text="Can restore from backups")
    can_manage_system = models.BooleanField(default=True, help_text="Can manage system settings")
    can_view_audit_logs = models.BooleanField(default=True, help_text="Can view complete audit logs")

    # Status
    is_active = models.BooleanField(default=True, help_text="Superadmin account is active")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Super Admin"
        verbose_name_plural = "Super Admins"

    def __str__(self):
        return f"SuperAdmin: {self.user.email}"


class DatabaseBackup(models.Model):
    """Track database backups created by superadmin."""

    created_by = models.ForeignKey(
        SuperAdmin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='backups_created'
    )

    backup_file = models.FileField(upload_to='backups/')
    backup_type = models.CharField(
        max_length=50,
        choices=[
            ('FULL', 'Full Database'),
            ('PARTIAL', 'Partial Tables'),
            ('ANALYTICS', 'Analytics Only'),
            ('AUDIT_LOG', 'Audit Log Only'),
        ],
        default='FULL'
    )

    description = models.TextField(blank=True)
    file_size_mb = models.FloatField(null=True, blank=True)
    table_count = models.IntegerField(default=0)
    record_count = models.IntegerField(default=0)

    is_verified = models.BooleanField(default=False, help_text="Backup verified and restorable")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Backup - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class DataExport(models.Model):
    """Track data exports performed by superadmin."""

    created_by = models.ForeignKey(
        SuperAdmin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exports_created'
    )

    export_file = models.FileField(upload_to='exports/')
    export_type = models.CharField(
        max_length=50,
        choices=[
            ('CSV', 'CSV Format'),
            ('EXCEL', 'Excel Format'),
            ('JSON', 'JSON Format'),
            ('PDF', 'PDF Report'),
        ]
    )

    tables_included = models.TextField(help_text="Comma-separated list of exported tables")
    record_count = models.IntegerField(default=0)
    file_size_mb = models.FloatField(null=True, blank=True)

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Export - {self.export_type} - {self.created_at.strftime('%Y-%m-%d')}"


class DataImport(models.Model):
    """Track bulk data imports performed by superadmin."""

    created_by = models.ForeignKey(
        SuperAdmin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='imports_created'
    )

    import_file = models.FileField(upload_to='imports/')
    import_type = models.CharField(
        max_length=50,
        choices=[
            ('STUDENTS', 'Students'),
            ('APPLICATIONS', 'Applications'),
            ('DOCUMENTS', 'Documents'),
            ('USERS', 'Users'),
            ('BULK', 'Bulk Mixed Data'),
        ]
    )

    status = models.CharField(
        max_length=50,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
            ('PARTIAL', 'Partially Completed'),
        ],
        default='PENDING'
    )

    total_records = models.IntegerField(default=0)
    successful_records = models.IntegerField(default=0)
    failed_records = models.IntegerField(default=0)

    error_details = models.TextField(blank=True, help_text="Details of any import errors")

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Import - {self.import_type} - {self.status}"


class SuperAdminAuditLog(models.Model):
    """Detailed audit log of all superadmin actions."""

    superadmin = models.ForeignKey(
        SuperAdmin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    action = models.CharField(
        max_length=100,
        choices=[
            ('LOGIN', 'Superadmin Login'),
            ('LOGOUT', 'Superadmin Logout'),
            ('USER_CREATE', 'Created User'),
            ('USER_DELETE', 'Deleted User'),
            ('USER_UPDATE', 'Updated User'),
            ('BRANCH_CREATE', 'Created Branch'),
            ('BRANCH_DELETE', 'Deleted Branch'),
            ('DATABASE_BACKUP', 'Created Backup'),
            ('DATABASE_RESTORE', 'Restored Database'),
            ('DATA_EXPORT', 'Exported Data'),
            ('DATA_IMPORT', 'Imported Data'),
            ('BULK_DELETE', 'Bulk Delete'),
            ('PERMISSIONS_CHANGE', 'Changed Permissions'),
            ('SYSTEM_SETTING', 'Changed System Setting'),
            ('FAILED_ACTION', 'Failed Action'),
        ]
    )

    description = models.TextField(blank=True)
    affected_records = models.IntegerField(default=0, help_text="Number of records affected")
    status = models.CharField(
        max_length=20,
        choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')],
        default='SUCCESS'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['superadmin', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class DatabaseStatistics(models.Model):
    """Snapshot of database statistics for monitoring."""

    timestamp = models.DateTimeField(auto_now_add=True)

    # Table counts
    total_users = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)
    total_applications = models.IntegerField(default=0)
    total_documents = models.IntegerField(default=0)
    total_followups = models.IntegerField(default=0)
    total_branches = models.IntegerField(default=0)

    # Record counts by status
    active_students = models.IntegerField(default=0)
    archived_students = models.IntegerField(default=0)
    verified_students = models.IntegerField(default=0)

    pending_applications = models.IntegerField(default=0)
    approved_applications = models.IntegerField(default=0)
    rejected_applications = models.IntegerField(default=0)
    visa_granted_applications = models.IntegerField(default=0)

    pending_documents = models.IntegerField(default=0)
    approved_documents = models.IntegerField(default=0)

    pending_followups = models.IntegerField(default=0)
    completed_followups = models.IntegerField(default=0)

    # Activity
    logins_today = models.IntegerField(default=0)
    actions_today = models.IntegerField(default=0)

    # Database health
    database_size_mb = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"Database Stats - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
