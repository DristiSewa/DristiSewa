import re

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.permissions import role_required
from core.services import filter_by_branch
from .forms import StudentEditForm, StudentProfileForm, StudentRegistrationForm
from .models import Student

User = get_user_model()


@role_required("STUDENT")
def profile(request):
    student, _ = Student.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("students:profile")
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentProfileForm(instance=student)

    return render(request, "students/profile.html", {"form": form, "student": student})


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def student_management(request):
    students = Student.objects.select_related("user", "user__branch").filter(is_archived=False)
    students = filter_by_branch(request.user, students, branch_field="user__branch")

    query = request.GET.get("q", "").strip()
    if query:
        students = (
            students.filter(user__email__icontains=query)
            | students.filter(user__first_name__icontains=query)
            | students.filter(user__last_name__icontains=query)
        )

    return render(request, "students/student_management.html", {"students": students.distinct(), "query": query})


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def archived_students(request):
    students = Student.objects.select_related("user", "user__branch").filter(is_archived=True)
    students = filter_by_branch(request.user, students, branch_field="user__branch")

    query = request.GET.get("q", "").strip()
    if query:
        students = (
            students.filter(user__email__icontains=query)
            | students.filter(user__first_name__icontains=query)
            | students.filter(user__last_name__icontains=query)
        )

    from reports.services import dashboard_summary

    return render(
        request,
        "dashboards/archived_students.html",
        {"students": students.distinct(), "query": query, "summary": dashboard_summary(request.user)},
    )


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def student_profile_view(request, pk):
    student = get_object_or_404(
        filter_by_branch(
            request.user,
            Student.objects.select_related("user", "user__branch").prefetch_related(
                "documents", "followups", "appointments"
            ),
            branch_field="user__branch",
        ),
        pk=pk,
    )

    if request.method == "POST" and "assign_user" in request.POST:
        assignee_id = request.POST.get("assigned_to")
        if assignee_id:
            assignee = get_object_or_404(User, pk=assignee_id, branch=student.user.branch)
            student.assigned_to = assignee
            student.assigned_by = request.user  # record who made the assignment
            student.save(update_fields=["assigned_to", "assigned_by"])
            messages.success(request, f"Assigned {assignee.get_full_name() or assignee.email} to this student.")
        else:
            student.assigned_to = None
            student.assigned_by = None
            student.save(update_fields=["assigned_to", "assigned_by"])
            messages.success(request, "Removed user assignment.")
        return redirect("students:student_profile", pk=student.pk)

    if request.method == "POST" and "edit_profile_modal" in request.POST:
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = User.objects.normalize_email(request.POST.get("email", "").strip()).lower()
        phone = request.POST.get("phone", "").strip()
        preferred_country = request.POST.get("preferred_country", "").strip()
        test_type = request.POST.get("test_type", "").strip()
        test_score = request.POST.get("test_score", "").strip()

        valid_countries = {
            "Australia",
            "Canada",
            "New Zealand",
            "United Kingdom",
            "United States",
        }
        errors = []
        name_pattern = re.compile(r"^[A-Za-z][A-Za-z\s'-]{1,49}$")

        if not first_name:
            errors.append("First name is required.")
        elif not name_pattern.fullmatch(first_name):
            errors.append("First name must be 2 to 50 letters and may only include spaces, apostrophes, or hyphens.")
        if not last_name:
            errors.append("Last name is required.")
        elif not name_pattern.fullmatch(last_name):
            errors.append("Last name must be 2 to 50 letters and may only include spaces, apostrophes, or hyphens.")
        if not email:
            errors.append("Email address is required.")
        elif len(email) > 254 or any(char.isspace() for char in email):
            errors.append("Enter a valid email address.")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Enter a valid email address.")
            if User.objects.exclude(pk=student.user_id).filter(email__iexact=email).exists():
                errors.append("Another user already uses this email address.")
        if not phone:
            errors.append("Phone number is required.")
        elif not phone.isdigit() or len(phone) < 7 or len(phone) > 15:
            errors.append("Phone number must contain 7 to 15 digits.")
        elif len(set(phone)) == 1:
            errors.append("Phone number cannot use the same digit repeatedly.")
        if preferred_country not in valid_countries:
            errors.append("Please choose a valid preferred country.")
        score_rules = {
            Student.Test.IELTS: (0, 9, "IELTS score must be between 0 and 9."),
            Student.Test.PTE: (10, 90, "PTE score must be between 10 and 90."),
            Student.Test.TOEFL: (0, 120, "TOEFL score must be between 0 and 120."),
        }

        if test_type not in dict(Student.Test.choices):
            errors.append("Please choose a valid test type.")
        if not test_score:
            errors.append("Score is required.")
        else:
            try:
                score_value = float(test_score)
                if test_type in score_rules:
                    min_score, max_score, message = score_rules[test_type]
                    if score_value < min_score or score_value > max_score:
                        errors.append(message)
                    elif test_type == Student.Test.IELTS and (score_value * 2) % 1 != 0:
                        errors.append("IELTS score must use 0.5 bands, for example 6.5 or 7.")
            except ValueError:
                errors.append("Score must be a valid number.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect(f"{reverse('students:student_profile', kwargs={'pk': student.pk})}?edit=1")
        else:
            user = student.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone
            user.save(update_fields=["first_name", "last_name", "email", "phone"])

            student.preferred_country = preferred_country
            student.test_type = test_type
            student.test_score = test_score
            student.save(update_fields=["preferred_country", "test_type", "test_score"])
            messages.success(request, "Student profile updated.")

        return redirect("students:student_profile", pk=student.pk)

    if request.method == "POST" and "update_doc_status" in request.POST:
        from documents.models import Document

        document = get_object_or_404(Document, pk=request.POST.get("document_id"), student=student)
        new_status = request.POST.get("status")
        if new_status in dict(Document.Status.choices):
            document.status = new_status
            document.save(update_fields=["status"])
            messages.success(request, "Document status updated.")
        return redirect("students:student_profile", pk=student.pk)

    if request.method == "POST" and "add_remark" in request.POST:
        from followups.models import FollowUp

        scheduled_date = request.POST.get("scheduled_date") or None
        note = request.POST.get("note", "").strip()
        if not note:
            note = (
                f"Followup added successfully for {scheduled_date}."
                if scheduled_date
                else "Followup added successfully."
            )
        if request.user.role == User.Role.FRONTDESK:
            # Front-desk notes are a chronological communication history.
            FollowUp.objects.create(
                student=student,
                assigned_to=request.user,
                scheduled_date=scheduled_date,
                note=note,
            )
            messages.success(request, "Remark added.")
        else:
            FollowUp.objects.update_or_create(
                student=student,
                defaults={
                    "assigned_to": request.user,
                    "scheduled_date": scheduled_date,
                    "note": note,
                    "is_done": False,
                },
            )
            messages.success(request, "Follow-up saved.")
        return redirect(f"{reverse('students:student_profile', kwargs={'pk': student.pk})}?tab=remarks")

    if request.method == "POST" and "remove_remark" in request.POST:
        from followups.models import FollowUp

        followup = get_object_or_404(FollowUp, pk=request.POST.get("followup_id"), student=student)
        followup.delete()
        messages.success(request, "Remark removed.")
        return redirect(f"{reverse('students:student_profile', kwargs={'pk': student.pk})}?tab=remarks")

    if request.method == "POST" and "upload_document" in request.POST:
        from documents.forms import DocumentUploadForm

        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student
            document.save()
            messages.success(request, "Document uploaded.")
        else:
            messages.error(request, "Please correct the errors and try again.")
        return redirect("students:student_profile", pk=student.pk)

    from documents.forms import DocumentUploadForm
    from documents.models import Document

    documents = student.documents.all() if hasattr(student, "documents") else []
    followups = student.followups.all() if hasattr(student, "followups") else []
    appointments = student.appointments.all() if hasattr(student, "appointments") else []

    # Frontdesk assigns student to a Manager only
    assignable_users = User.objects.filter(
        branch=student.user.branch, role=User.Role.MANAGER
    ).order_by("first_name", "last_name")

    return render(
        request,
        "dashboards/student_profile.html",
        {
            "student": student,
            "documents": documents,
            "followups": followups,
            "appointments": appointments,
            "assignable_users": assignable_users,
            "doc_statuses": Document.Status.choices,
            "upload_form": DocumentUploadForm(),
            "today": timezone.localdate(),
        },
    )


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def student_verify(request, pk):
    student = get_object_or_404(
        filter_by_branch(request.user, Student.objects.select_related("user"), branch_field="user__branch"),
        pk=pk,
    )
    student.is_verified = True
    student.save(update_fields=["is_verified"])
    messages.success(request, "Student marked as verified.")
    if request.user.role == User.Role.FRONTDESK:
        return redirect("accounts:frontdesk_dashboard")
    return redirect("students:student_management")


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def student_archive(request, pk):
    student = get_object_or_404(
        filter_by_branch(request.user, Student.objects.select_related("user"), branch_field="user__branch"),
        pk=pk,
    )
    student.is_archived = True
    student.save(update_fields=["is_archived"])
    messages.success(request, "Student archived.")
    if request.user.role == User.Role.FRONTDESK:
        return redirect("accounts:frontdesk_dashboard")
    return redirect("students:student_management")


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def student_unarchive(request, pk):
    student = get_object_or_404(
        filter_by_branch(request.user, Student.objects.select_related("user"), branch_field="user__branch"),
        pk=pk,
    )
    student.is_archived = False
    student.save(update_fields=["is_archived"])
    messages.success(request, "Student restored.")
    return redirect("students:archived_students")


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def student_create(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            branch = request.user.branch if request.user.role == User.Role.FRONTDESK else None
            form.save(branch=branch)
            messages.success(request, "Student registered successfully.")
            if request.user.role == User.Role.FRONTDESK:
                return redirect("accounts:frontdesk_dashboard")
            return redirect("students:student_management")
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentRegistrationForm()

    return render(request, "students/student_form.html", {"form": form, "mode": "create"})


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def student_edit(request, pk):
    student = get_object_or_404(
        filter_by_branch(request.user, Student.objects.select_related("user"), branch_field="user__branch"),
        pk=pk,
    )

    if request.method == "POST":
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            if request.user.role == User.Role.FRONTDESK:
                return redirect("accounts:frontdesk_dashboard")
            return redirect("students:student_management")
        messages.error(request, "Please correct the errors below.")
    else:
        form = StudentEditForm(instance=student)

    return render(request, "students/student_form.html", {"form": form, "mode": "edit", "student": student})


@require_POST
@role_required("STUDENT")
def upload_profile_pic(request):
    student, _ = Student.objects.get_or_create(user=request.user)
    pic = request.FILES.get("profile_pic")
    if not pic:
        return JsonResponse({"success": False, "error": "No file provided."})
    allowed = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if pic.content_type not in allowed:
        return JsonResponse({"success": False, "error": "Only JPG, PNG, WEBP or GIF allowed."})
    student.profile_pic = pic
    student.save(update_fields=["profile_pic"])
    return JsonResponse({"success": True, "url": student.profile_pic.url})
