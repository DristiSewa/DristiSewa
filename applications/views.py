from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required
from core.services import filter_by_branch, pipeline_counts
from documents.forms import DocumentUploadForm
from documents.models import Document
from students.models import Student
from .forms import ApplicationCreateForm, ApplicationForm, ApplicationStudentForm
from .models import Application


@role_required("STUDENT")
def app_status(request):
    student, _ = Student.objects.get_or_create(user=request.user)
    applications = student.applications.all()
    documents = student.documents.all()

    if request.method == "POST":
        doc_form = DocumentUploadForm(request.POST, request.FILES)
        if doc_form.is_valid():
            doc = doc_form.save(commit=False)
            doc.student = student
            doc.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect("applications:app_status")
        messages.error(request, "Please correct the errors below.")
    else:
        doc_form = DocumentUploadForm()

    return render(
        request,
        "applications/app_status.html",
        {"applications": applications, "documents": documents, "doc_form": doc_form},
    )


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def application_list(request):
    applications = Application.objects.select_related("student__user", "student__user__branch")
    applications = filter_by_branch(request.user, applications, branch_field="student__user__branch")

    status_filter = request.GET.get("status", "")
    if status_filter:
        applications = applications.filter(status=status_filter)

    return render(
        request,
        "applications/application_list.html",
        {
            "applications": applications,
            "statuses": Application.Status.choices,
            "status_filter": status_filter,
            "pipeline": pipeline_counts(applications, choices=Application.Status.choices),
        },
    )


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def application_create(request):
    students = filter_by_branch(request.user, Student.objects.select_related("user"), branch_field="user__branch")

    if request.method == "POST":
        form = ApplicationCreateForm(request.POST)
        form.fields["student"].queryset = students
        if form.is_valid():
            form.save()
            messages.success(request, "Application created.")
            return redirect("applications:application_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ApplicationCreateForm()
        form.fields["student"].queryset = students

    return render(request, "applications/application_create.html", {"form": form})


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def application_update(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if request.method == "POST":
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated.")
            return redirect("applications:application_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ApplicationForm(instance=application)

    return render(request, "applications/application_form.html", {"form": form, "application": application})
