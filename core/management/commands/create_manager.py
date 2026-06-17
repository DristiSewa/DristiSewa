from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from branches.models import Branch

User = get_user_model()

DEFAULT_EMAIL = "manager@dristisewa.com"
DEFAULT_PASSWORD = "Manager@123"


class Command(BaseCommand):
    help = (
        "Creates (or resets) a temporary Manager account for testing the "
        "manager dashboard. Usage: python manage.py create_manager "
        "[--email EMAIL] [--password PASSWORD]"
    )

    def add_arguments(self, parser):
        parser.add_argument("--email", default=DEFAULT_EMAIL)
        parser.add_argument("--password", default=DEFAULT_PASSWORD)

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]

        branch = Branch.objects.first()

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": "Test",
                "last_name": "Manager",
                "role": User.Role.MANAGER,
                "branch": branch,
                "is_staff": True,
            },
        )

        user.role = User.Role.MANAGER
        user.is_staff = True
        if branch and not user.branch:
            user.branch = branch
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created manager account: {email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated existing account to manager: {email}"))

        self.stdout.write(self.style.SUCCESS(f"Email: {email}"))
        self.stdout.write(self.style.SUCCESS(f"Password: {password}"))
        self.stdout.write("Login at the staff login page (/staff-login/ or similar) and select role 'Manager'.")
