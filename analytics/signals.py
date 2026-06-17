from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from accounts.models import User
from applications.models import Application
from documents.models import Document
from followups.models import FollowUp
from students.models import Student

from .models import DetailedActivityLog


@receiver(post_save, sender=Student)
def log_student_changes(sender, instance, created, **kwargs):
    """Log student creation and updates."""
    if created:
        DetailedActivityLog.objects.create(
            user=None,
            action=DetailedActivityLog.Action.STUDENT_CREATE,
            description=f"Student {instance.user.email} created",
            entity_type='Student',
            entity_id=str(instance.id),
            branch=instance.user.branch,
        )


@receiver(post_save, sender=Application)
def log_application_changes(sender, instance, created, **kwargs):
    """Log application creation and status changes."""
    if created:
        DetailedActivityLog.objects.create(
            action=DetailedActivityLog.Action.APPLICATION_CREATE,
            description=f"Application created for {instance.student.user.email}",
            entity_type='Application',
            entity_id=str(instance.id),
            branch=instance.student.user.branch,
        )
    else:
        DetailedActivityLog.objects.create(
            action=DetailedActivityLog.Action.APPLICATION_UPDATE,
            description=f"Application status updated to {instance.get_status_display()}",
            entity_type='Application',
            entity_id=str(instance.id),
            branch=instance.student.user.branch,
        )


@receiver(post_save, sender=Document)
def log_document_changes(sender, instance, created, **kwargs):
    """Log document uploads and status changes."""
    if created:
        DetailedActivityLog.objects.create(
            action=DetailedActivityLog.Action.DOCUMENT_UPLOAD,
            description=f"Document uploaded: {instance.get_doc_type_display()}",
            entity_type='Document',
            entity_id=str(instance.id),
            branch=instance.student.user.branch,
        )
    else:
        DetailedActivityLog.objects.create(
            action=DetailedActivityLog.Action.DOCUMENT_APPROVE,
            description=f"Document status: {instance.get_status_display()}",
            entity_type='Document',
            entity_id=str(instance.id),
            branch=instance.student.user.branch,
        )


@receiver(post_save, sender=FollowUp)
def log_followup_changes(sender, instance, created, **kwargs):
    """Log follow-up creation and completion."""
    if created:
        DetailedActivityLog.objects.create(
            user=instance.assigned_to,
            action=DetailedActivityLog.Action.FOLLOWUP_CREATE,
            description=f"Follow-up created for {instance.student.user.email}",
            entity_type='FollowUp',
            entity_id=str(instance.id),
            branch=instance.student.user.branch,
        )
