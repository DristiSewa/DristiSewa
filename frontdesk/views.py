from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required
from applications.models import Application
from core.services import filter_by_branch
from students.forms import StudentEditForm
from students.models import Student

from .forms import ApplicationStatusUpdateForm


def _get_branch_scoped_student(request, pk):
    """Fetch a single student, scoped to the front-desk user's branch."""
    queryset = Student.objects.select_related("user", "user__branch")
    queryset = filter_by_branch(request.user, queryset, branch_field="user__branch")
    return get_object_or_404(queryset, pk=pk)


@role_required("FRONTDESK")
def student_list(request):
    """List/search/filter students (Front Desk)."""
    students = Student.objects.select_related("user", "user__branch").all()
    students = filter_by_branch(request.user, students, branch_field="user__branch")

    query = request.GET.get("q", "").strip()
    if query:
        matches = (
            students.filter(user__email__icontains=query)
            | students.filter(user__first_name__icontains=query)
            | students.filter(user__last_name__icontains=query)
            | students.filter(user__phone__icontains=query)
        )
        if query.isdigit():
            matches = matches | students.filter(id=query)
        students = matches

    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        students = students.filter(applications__status=status_filter)

    country_filter = request.GET.get("country", "").strip()
    if country_filter:
        students = students.filter(preferred_country__icontains=country_filter)

    students = students.distinct().order_by("user__first_name", "user__last_name")

    paginator = Paginator(students, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "frontdesk/student_list.html",
        {
            "page_obj": page_obj,
            "students": page_obj.object_list,
            "query": query,
            "status_filter": status_filter,
            "country_filter": country_filter,
            "statuses": Application.Status.choices,
        },
    )


@role_required("FRONTDESK")
def student_detail(request, pk):
    """View a single student's full profile (Front Desk)."""
    student = _get_branch_scoped_student(request, pk)

    return render(
        request,
        "frontdesk/student_detail.html",
        {
            "student": student,
            "applications": student.applications.all(),
            "documents": student.documents.all(),
            "followups": student.followups.all(),
            "appointments": student.appointments.all(),
            "latest_application": student.applications.first(),
        },
    )


@role_required("FRONTDESK")
def student_edit(request, pk):
    """Edit personal/academic information for a student (Front Desk)."""
    student = _get_branch_scoped_student(request, pk)

    if request.method == "POST":
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect("frontdesk:student_detail", pk=student.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentEditForm(instance=student)

    return render(
        request,
        "frontdesk/student_edit.html",
        {"form": form, "student": student},
    )


@role_required("FRONTDESK")
def student_status_update(request, pk):
    """Update a student's application/pipeline status (Front Desk)."""
    student = _get_branch_scoped_student(request, pk)
    application = student.applications.first()

    if request.method == "POST":
        form = ApplicationStatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.student = student
            updated.save()
            messages.success(request, "Status updated successfully.")
            return redirect("frontdesk:student_detail", pk=student.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = ApplicationStatusUpdateForm(instance=application)

    return render(
        request,
        "frontdesk/student_status_form.html",
        {"form": form, "student": student, "application": application},
    )
