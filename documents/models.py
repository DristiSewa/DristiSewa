from django.db import models

from core.models import TimeStampedModel
from students.models import Student


class Document(TimeStampedModel):
    class DocType(models.TextChoices):
        PASSPORT = "PASSPORT", "Passport"
        TRANSCRIPT = "TRANSCRIPT", "Academic Transcript"
        CERTIFICATE = "CERTIFICATE", "Certificate"
        TEST_SCORE = "TEST_SCORE", "Test Score Report"
        BANK_STATEMENT = "BANK_STATEMENT", "Bank Statement"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DocType.choices, default=DocType.OTHER)
    file = models.FileField(upload_to="documents/")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.get_doc_type_display()}"
