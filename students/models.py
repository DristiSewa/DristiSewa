from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Student(TimeStampedModel):
    """Extended profile data for users with role=STUDENT."""

    class Test(models.TextChoices):
        IELTS = "IELTS", "IELTS"
        PTE = "PTE", "PTE"
        TOEFL = "TOEFL", "TOEFL"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_students",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_by_students",
    )
    date_of_birth = models.DateField(null=True, blank=True)
    college = models.CharField(max_length=200, blank=True)
    passed_year = models.PositiveIntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    test_type = models.CharField(max_length=10, choices=Test.choices, blank=True)
    test_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    preferred_country = models.CharField(max_length=100, blank=True)
    is_archived = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    profile_pic = models.ImageField(
        upload_to="profile_pics/", default="profile_pics/default.png", blank=True
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.email
