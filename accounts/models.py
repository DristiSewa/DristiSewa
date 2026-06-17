from .managers import UserManager
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import timedelta


class User(AbstractUser):
    """Single, unified identity model for every role in DristiSewa.

    `username` is removed; `email` is the login identifier (USERNAME_FIELD).
    Role-based access control is driven by the `role` field.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        FRONTDESK = "FRONTDESK", "Front Desk"
        STUDENT = "STUDENT", "Student"

    username = None
    email = models.EmailField("email address", unique=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.STUDENT)
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff",
    )
    phone = models.CharField(max_length=20, blank=True)
    experience_details = models.TextField(blank=True)
    profile_pic = models.ImageField(
        upload_to="profile_pics/", default="profile_pics/default.png", blank=True
    )
    last_seen = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_frontdesk(self):
        return self.role == self.Role.FRONTDESK

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_online(self):
        """A user is considered online if they made a request within the
        last few minutes (tracked via accounts.middleware.LastSeenMiddleware)."""
        if not self.last_seen:
            return False
        threshold = timezone.now() - timedelta(minutes=5)
        return self.last_seen >= threshold


class OTPVerification(models.Model):
    """Short-lived one-time-password used for registration/email verification
    and password resets. Keyed by email rather than a User FK because OTPs
    are issued *before* the account exists (registration flow)."""

    class Purpose(models.TextChoices):
        REGISTRATION = "REGISTRATION", "Registration"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20, choices=Purpose.choices, default=Purpose.REGISTRATION)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def is_expired(self):
        expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
        return timezone.now() > self.created_at + timedelta(minutes=expiry_minutes)

    def __str__(self):
        return f"{self.email} - {self.otp}"
