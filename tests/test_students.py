from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from applications.models import Application
from branches.models import Branch
from followups.models import FollowUp
from students.models import Student


class StudentProfileModalValidationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            role=User.Role.ADMIN,
        )
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Puspa",
            last_name="Pandit",
            phone="9814151727",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            preferred_country="United Kingdom",
            test_type=Student.Test.IELTS,
            test_score="8.00",
        )
        self.url = reverse("students:student_profile", args=[self.student.pk])

    def test_rejects_invalid_name_email_and_phone(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.url,
            {
                "edit_profile_modal": "1",
                "first_name": "Puspa123",
                "last_name": "P",
                "email": "not-an-email",
                "phone": "1111111",
                "preferred_country": "United Kingdom",
                "test_type": "IELTS",
                "test_score": "8.0",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("?edit=1", response["Location"])
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, "Puspa")
        self.assertEqual(self.student_user.email, "student@example.com")
        self.assertEqual(self.student_user.phone, "9814151727")

    def test_accepts_valid_profile_details(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.url,
            {
                "edit_profile_modal": "1",
                "first_name": "Anne-Marie",
                "last_name": "O'Neill",
                "email": "anne.oneill@example.com",
                "phone": "9814151728",
                "preferred_country": "Canada",
                "test_type": "PTE",
                "test_score": "65",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.student_user.refresh_from_db()
        self.student.refresh_from_db()
        self.assertEqual(self.student_user.first_name, "Anne-Marie")
        self.assertEqual(self.student_user.last_name, "O'Neill")
        self.assertEqual(self.student_user.email, "anne.oneill@example.com")
        self.assertEqual(self.student_user.phone, "9814151728")
        self.assertEqual(self.student.test_type, Student.Test.PTE)


class StudentApplicationStatusRemarksTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Kathmandu", code="KTM")
        self.manager = User.objects.create_user(
            email="manager.remarks@example.com",
            password="password123",
            role=User.Role.MANAGER,
            branch=self.branch,
        )
        self.student_user = User.objects.create_user(
            email="student.remarks@example.com",
            password="password123",
            role=User.Role.STUDENT,
            branch=self.branch,
        )
        self.student = Student.objects.create(user=self.student_user)
        Application.objects.create(
            student=self.student,
            destination_country="Canada",
            remarks="Application received.",
        )
        FollowUp.objects.create(
            student=self.student,
            assigned_to=self.manager,
            note="Please upload your bank statement.",
        )

    def test_manager_remark_is_shown_in_student_application_status(self):
        self.client.force_login(self.student_user)

        response = self.client.get(reverse("applications:app_status"))

        self.assertContains(response, "Please upload your bank statement.")
        self.assertContains(response, "Application received.")


class FrontDeskRemarkHistoryTests(TestCase):
    def test_a_student_can_have_multiple_frontdesk_remarks(self):
        frontdesk = User.objects.create_user(
            email="frontdesk.remarks@example.com",
            password="password123",
            role=User.Role.FRONTDESK,
        )
        student_user = User.objects.create_user(
            email="remark.history.student@example.com",
            password="password123",
            role=User.Role.STUDENT,
        )
        student = Student.objects.create(user=student_user)

        FollowUp.objects.create(student=student, assigned_to=frontdesk, note="First remark")
        FollowUp.objects.create(student=student, assigned_to=frontdesk, note="Second remark")

        self.assertEqual(student.followups.count(), 2)


class AdminStudentManagementCardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin.card@example.com",
            password="password123",
            role=User.Role.ADMIN,
        )
        self.branch = Branch.objects.create(name="Kathmandu", code="KTM")
        self.other_branch = Branch.objects.create(name="Pokhara", code="PKR")
        self.frontdesk = User.objects.create_user(
            email="frontdesk.card@example.com",
            password="password123",
            role=User.Role.FRONTDESK,
            branch=self.branch,
        )

    def _create_student(self, email, branch, assigned_to=None, assigned_by=None):
        user = User.objects.create_user(
            email=email,
            password="password123",
            role=User.Role.STUDENT,
            branch=branch,
            first_name=email.split("@")[0],
        )
        return Student.objects.create(user=user, assigned_to=assigned_to, assigned_by=assigned_by)

    def test_top_cards_count_all_branches_even_when_table_is_branch_filtered(self):
        branch_student = self._create_student(
            "branch.student@example.com",
            self.branch,
            assigned_to=self.frontdesk,
            assigned_by=self.frontdesk,
        )
        other_student = self._create_student("other.student@example.com", self.other_branch)
        terminal_student = self._create_student(
            "terminal.student@example.com",
            self.branch,
            assigned_to=self.frontdesk,
            assigned_by=self.frontdesk,
        )
        archived_student = self._create_student("archived.student@example.com", self.other_branch)
        archived_student.is_archived = True
        archived_student.save(update_fields=["is_archived"])
        FollowUp.objects.create(student=branch_student, assigned_to=self.frontdesk, note="Pending", is_done=False)
        FollowUp.objects.create(student=other_student, assigned_to=self.frontdesk, note="Done", is_done=True)
        FollowUp.objects.create(student=archived_student, assigned_to=self.frontdesk, note="Archived", is_done=False)
        Application.objects.create(student=terminal_student, status=Application.Status.VISA_GRANTED)
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse("accounts:student_management"),
            {"branch": str(self.branch.id)},
        )

        self.assertEqual(response.context["card_counts"]["all_students"], 3)
        self.assertEqual(response.context["card_counts"]["pending_followups"], 1)
        self.assertEqual(response.context["card_counts"]["completed_followups"], 2)
        self.assertEqual(response.context["card_counts"]["unassigned_students"], 1)
        self.assertEqual(len(response.context["students"]), 2)
        terminal_row = next(
            student for student in response.context["students"]
            if student["pk"] == terminal_student.pk
        )
        self.assertEqual(terminal_row["follow_up_status"], "completed")


class BranchStudentTrackerStatusTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Kathmandu", code="KTM")
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="password123",
            role=User.Role.MANAGER,
            branch=self.branch,
        )
        self.frontdesk = User.objects.create_user(
            email="frontdesk@example.com",
            password="password123",
            role=User.Role.FRONTDESK,
            branch=self.branch,
        )
        self.student_user = User.objects.create_user(
            email="verified.student@example.com",
            password="password123",
            role=User.Role.STUDENT,
            branch=self.branch,
            first_name="Verified",
            last_name="Student",
        )
        self.student = Student.objects.create(
            user=self.student_user,
            assigned_to=self.frontdesk,
            is_verified=True,
        )

    def test_branch_tracker_status_does_not_use_student_verification(self):
        FollowUp.objects.create(
            student=self.student,
            assigned_to=self.frontdesk,
            note="Call student",
            is_done=False,
        )
        self.client.force_login(self.manager)

        response = self.client.get(reverse("accounts:branch_monitoring"))

        self.assertEqual(response.status_code, 200)
        tracked_student = next(
            student for student in response.context["branch_students"]
            if student["id"] == self.student.id
        )
        self.assertEqual(tracked_student["tracking"], "pending")

    def test_terminal_application_status_completes_branch_tracker(self):
        FollowUp.objects.create(
            student=self.student,
            assigned_to=self.frontdesk,
            note="Call student",
            is_done=False,
        )
        Application.objects.create(
            student=self.student,
            status=Application.Status.VISA_GRANTED,
        )
        self.client.force_login(self.manager)

        response = self.client.get(reverse("accounts:branch_monitoring"))

        self.assertEqual(response.status_code, 200)
        tracked_student = next(
            student for student in response.context["branch_students"]
            if student["id"] == self.student.id
        )
        self.assertEqual(tracked_student["tracking"], "completed")
        self.assertEqual(response.context["completed_trackers"], 1)
        self.assertEqual(response.context["pending_trackers"], 0)

    def test_pending_followups_bar_counts_all_students_with_pending_tracker_status(self):
        self.student.assigned_to = self.manager
        self.student.assigned_by = self.frontdesk
        self.student.save(update_fields=["assigned_to", "assigned_by"])
        second_student_user = User.objects.create_user(
            email="second.student@example.com",
            password="password123",
            role=User.Role.STUDENT,
            branch=self.branch,
            first_name="Second",
            last_name="Student",
        )
        second_student = Student.objects.create(
            user=second_student_user,
            assigned_to=self.manager,
            assigned_by=self.frontdesk,
        )
        no_followup_user = User.objects.create_user(
            email="no.followup@example.com",
            password="password123",
            role=User.Role.STUDENT,
            branch=self.branch,
            first_name="No",
            last_name="Followup",
        )
        Student.objects.create(
            user=no_followup_user,
            assigned_to=self.manager,
            assigned_by=self.frontdesk,
        )
        FollowUp.objects.create(
            student=self.student,
            assigned_to=self.frontdesk,
            note="Call student",
            is_done=False,
        )
        FollowUp.objects.create(
            student=second_student,
            assigned_to=self.frontdesk,
            note="Call second student",
            is_done=False,
        )
        self.client.force_login(self.manager)

        response = self.client.get(reverse("accounts:followup_management"))

        self.assertEqual(response.context["pending_trackers"], 3)
        self.assertEqual(response.context["completed_trackers"], 0)

    def test_followup_management_excludes_students_not_handed_to_manager_by_frontdesk(self):
        handed_off_user = User.objects.create_user(
            email="handed.off@example.com",
            password="password123",
            role=User.Role.STUDENT,
            branch=self.branch,
            first_name="Handed",
            last_name="Off",
        )
        handed_off_student = Student.objects.create(
            user=handed_off_user,
            assigned_to=self.manager,
            assigned_by=self.frontdesk,
        )
        self.client.force_login(self.manager)

        response = self.client.get(reverse("accounts:followup_management"))

        student_ids = [student["id"] for student in response.context["students"]]
        self.assertIn(handed_off_student.id, student_ids)
        self.assertNotIn(self.student.id, student_ids)

    def test_manager_unassigned_bar_counts_students_not_handed_to_manager_by_frontdesk(self):
        frontdesk_assigned_user = User.objects.create_user(
            email="frontdesk.assigned.student@example.com",
            password="password123",
            role=User.Role.STUDENT,
            branch=self.branch,
            first_name="Frontdesk",
            last_name="Assigned",
        )
        Student.objects.create(
            user=frontdesk_assigned_user,
            assigned_to=self.frontdesk,
        )
        self.client.force_login(self.manager)

        response = self.client.get(reverse("accounts:branch_monitoring"))

        self.assertEqual(response.context["assigned_students_count"], 0)
        self.assertEqual(response.context["unassigned_students_count"], 2)

    def test_followup_management_terminal_status_marks_followup_complete(self):
        self.student.assigned_to = self.manager
        self.student.assigned_by = self.frontdesk
        self.student.save(update_fields=["assigned_to", "assigned_by"])
        followup = FollowUp.objects.create(
            student=self.student,
            assigned_to=self.frontdesk,
            note="Call student",
            is_done=False,
        )
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("accounts:followup_management"),
            {"student_id": self.student.id, "status": "Rejected"},
        )

        self.assertEqual(response.status_code, 302)
        followup.refresh_from_db()
        self.assertTrue(followup.is_done)

        response = self.client.get(reverse("accounts:followup_management"))
        self.assertEqual(response.context["completed_trackers"], 1)
        self.assertEqual(response.context["pending_trackers"], 0)
