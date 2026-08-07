import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from documents.models import Document
from students.models import Student


class DocumentFileViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._media_root = tempfile.mkdtemp()
        cls._override_media = override_settings(MEDIA_ROOT=cls._media_root)
        cls._override_media.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override_media.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com",
            password="password123",
            role=User.Role.STUDENT,
        )
        self.student = Student.objects.create(user=self.user)
        self.document = Document.objects.create(
            student=self.student,
            doc_type=Document.DocType.TRANSCRIPT,
            file=SimpleUploadedFile("transcript.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
        )

    def test_student_can_preview_own_document_inline(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("documents:document_preview", args=[self.document.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("inline", response["Content-Disposition"])
        self.assertEqual(response["X-Frame-Options"], "SAMEORIGIN")

    def test_student_can_download_own_document_as_attachment(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("documents:document_download", args=[self.document.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])

    def test_my_documents_does_not_show_a_remarks_column(self):
        self.document.remarks = "Please submit a clearer transcript."
        self.document.save(update_fields=["remarks"])
        self.client.force_login(self.user)

        response = self.client.get(reverse("documents:upload_docs"))

        self.assertNotContains(response, "Remarks")
        self.assertNotContains(response, "Please submit a clearer transcript.")
