from django.db import models

from core.models import TimeStampedModel
from students.models import Student


class Application(TimeStampedModel):
    """Tracks a student's visa/admission pipeline progress."""

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        APPLIED_OFFER_LETTER = "APPLIED_OFFER_LETTER", "Applied for Offer Letter"
        OFFER_LETTER_RECEIVED = "OFFER_LETTER_RECEIVED", "Offer Letter Received"
        COE_APPLIED = "COE_APPLIED", "COE Applied"
        COE_RECEIVED = "COE_RECEIVED", "COE Received"
        VISA_GRANTED = "VISA_GRANTED", "Visa Granted"
        REJECTED = "REJECTED", "Rejected"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="applications")
    destination_country = models.CharField(max_length=100, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"
