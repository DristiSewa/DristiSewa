from applications.models import Application
from core.services import filter_by_branch, pipeline_counts
from documents.models import Document
from followups.models import Appointment, FollowUp
from students.models import Student


def dashboard_summary(user):
    """Aggregate counts used across the staff dashboards, scoped to the
    requesting user's branch (ADMIN/MANAGER see everything)."""

    students = filter_by_branch(user, Student.objects.all(), branch_field="user__branch")
    applications = filter_by_branch(user, Application.objects.all(), branch_field="student__user__branch")
    documents = filter_by_branch(user, Document.objects.all(), branch_field="student__user__branch")
    followups = filter_by_branch(user, FollowUp.objects.all(), branch_field="student__user__branch")
    appointments = filter_by_branch(user, Appointment.objects.all(), branch_field="student__user__branch")

    return {
        "total_students": students.count(),
        "total_applications": applications.count(),
        "pending_documents": documents.filter(status=Document.Status.PENDING).count(),
        "pending_followups": followups.filter(is_done=False).count(),
        "pending_appointments": appointments.filter(
            status__in=[Appointment.Status.SCHEDULED, Appointment.Status.RESCHEDULED]
        ).count(),
        "pipeline": pipeline_counts(applications, choices=Application.Status.choices),
    }
