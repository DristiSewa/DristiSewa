from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from branches.models import Branch

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Creates a 'Main Branch' (if it doesn't exist) and assigns it to "
        "any user that doesn't currently belong to a branch. Useful for "
        "fixing empty branch-scoped lists (e.g. Front Desk student list) "
        "on freshly seeded databases."
    )

    def handle(self, *args, **options):
        branch, created = Branch.objects.get_or_create(
            code="MAIN",
            defaults={"name": "Main Branch", "is_active": True},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created branch: {branch.name}"))
        else:
            self.stdout.write(f"Using existing branch: {branch.name}")

        updated = User.objects.filter(branch__isnull=True).update(branch=branch)
        self.stdout.write(self.style.SUCCESS(f"Assigned {updated} user(s) to {branch.name}"))
