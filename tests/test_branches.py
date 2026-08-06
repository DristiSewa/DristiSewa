import json

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from branches.models import Branch


class UpdateBranchTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            role=User.Role.ADMIN,
        )
        self.branch = Branch.objects.create(name="Kaski DristiSewa", code="KSK")
        self.client.force_login(self.admin)

    def test_admin_can_update_a_branch_from_the_card_endpoint(self):
        response = self.client.post(
            reverse("branches:update_branch_json", args=[self.branch.id]),
            data=json.dumps({"branch_name": "Pokhara DristiSewa", "location": "Pokhara", "is_active": False}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": True,
            "branch_id": self.branch.id,
            "name": "Pokhara DristiSewa",
            "address": "Pokhara",
            "is_active": False,
        })
        self.branch.refresh_from_db()
        self.assertEqual(self.branch.name, "Pokhara DristiSewa")
        self.assertEqual(self.branch.address, "Pokhara")
        self.assertFalse(self.branch.is_active)
