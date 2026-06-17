from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import Application
from documents.models import Document
from followups.models import FollowUp
from students.models import Student

from .models import ActivityLog


@receiver(post_save, sender=Student)
def log_student_saved(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.user,
            action="STUDENT_PROFILE_CREATED",
            description=f"Student profile created for {instance.user.email}.",
        )


@receiver(post_save, sender=Application)
def log_application_saved(sender, instance, created, **kwargs):
    action = "APPLICATION_CREATED" if created else "APPLICATION_UPDATED"
    ActivityLog.objects.create(
        user=instance.student.user,
        action=action,
        description=f"Application for {instance.student.user.email} is now {instance.get_status_display()}.",
    )


@receiver(post_save, sender=Document)
def log_document_saved(sender, instance, created, **kwargs):
    action = "DOCUMENT_UPLOADED" if created else "DOCUMENT_UPDATED"
    ActivityLog.objects.create(
        user=instance.student.user,
        action=action,
        description=f"{instance.get_doc_type_display()} for {instance.student.user.email} is {instance.get_status_display()}.",
    )


@receiver(post_save, sender=FollowUp)
def log_followup_saved(sender, instance, created, **kwargs):
    action = "FOLLOWUP_CREATED" if created else "FOLLOWUP_UPDATED"
    ActivityLog.objects.create(
        user=instance.assigned_to,
        action=action,
        description=f"Follow-up for {instance.student.user.email} {'completed' if instance.is_done else 'scheduled'}.",
    )
