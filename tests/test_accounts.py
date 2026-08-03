from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from branches.models import Branch


class StaffLoginMessageTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Kathmandu", code="KTM")
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="password123",
            role=User.Role.MANAGER,
            branch=self.branch,
        )

    def test_staff_logout_does_not_show_work_notification_on_login_page(self):
        self.client.force_login(self.manager)

        self.client.post(
            reverse("accounts:front_desk"),
            {
                "form_action": "create",
                "name": "Nikita Thapa",
                "email": "nikita@example.com",
                "password": "password123",
            },
        )
        response = self.client.get(reverse("accounts:logout"), follow=True)

        self.assertEqual(response.resolver_match.url_name, "staff_login")
        self.assertNotContains(response, "Front desk account created for Nikita Thapa.")

    def test_staff_login_post_still_shows_login_errors(self):
        response = self.client.post(
            reverse("accounts:staff_login"),
            {
                "role": User.Role.MANAGER,
                "email": "manager@example.com",
                "password": "wrong-password",
            },
        )

        self.assertContains(response, "Invalid email or password.")
