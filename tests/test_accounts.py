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

    def test_front_desk_staff_without_photo_uses_name_initials(self):
        frontdesk = User.objects.create_user(
            email="nikita.rana@example.com",
            password="password123",
            first_name="Nikita",
            last_name="Rana",
            role=User.Role.FRONTDESK,
            branch=self.branch,
        )
        self.client.force_login(self.manager)

        response = self.client.get(reverse("accounts:front_desk"))

        self.assertContains(response, "NR")
        self.assertNotContains(response, "profile_pics/default.png")
        self.assertEqual(frontdesk.profile_pic.name, "profile_pics/default.png")


class AdminReportDownloadTests(TestCase):
    def test_admin_can_download_overall_report_as_pdf(self):
        admin = User.objects.create_user(
            email="admin.report@example.com",
            password="password123",
            role=User.Role.ADMIN,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("accounts:admin_download_report"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment; filename=", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))
