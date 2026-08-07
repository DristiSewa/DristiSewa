from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from students.models import Student


class FollowUp(TimeStampedModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="followups")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="followups"
    )
    note = models.TextField()
    scheduled_date = models.DateField(null=True, blank=True)
    is_done = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.scheduled_date or 'unscheduled'}"


class Appointment(TimeStampedModel):
    """A scheduled meeting between a student and staff (separate from
    follow-up/consultation notes)."""

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        RESCHEDULED = "RESCHEDULED", "Rescheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="appointments")
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments"
    )
    purpose = models.CharField(max_length=200, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-appointment_date", "-appointment_time"]

    def __str__(self):
        return f"{self.student} - {self.appointment_date} {self.appointment_time}"
