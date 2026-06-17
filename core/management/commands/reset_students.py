from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import OTPVerification

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Deletes all STUDENT users (and their related Student profiles, "
        "applications, documents, etc. via cascade) plus any pending "
        "OTPVerification records, so registration can be tested from "
        "scratch."
    )

    def handle(self, *args, **options):
        students = User.objects.filter(role=User.Role.STUDENT)
        count = students.count()
        for user in students:
            self.stdout.write(f"Deleting student: {user.email}")
        students.delete()

        otp_count, _ = OTPVerification.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted {count} student account(s)."))
        self.stdout.write(self.style.SUCCESS(f"Deleted {otp_count} OTP record(s)."))
