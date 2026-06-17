import logging
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

logger = logging.getLogger(__name__)

from .forms import LoginForm, OTPForm, RegisterForm, StaffLoginForm
from .models import OTPVerification
from .permissions import role_required

User = get_user_model()


def home(request):
    """Public landing page.

    Authenticated users are sent to their role's dashboard; everyone else
    sees the marketing landing page with links to login/register.
    """
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return render(request, "home.html")


def _generate_and_send_otp(email):
    otp_length = getattr(settings, "OTP_LENGTH", 6)
    expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 5)

    otp = f"{random.randint(0, 10 ** otp_length - 1):0{otp_length}d}"
    OTPVerification.objects.create(email=email, otp=otp, purpose=OTPVerification.Purpose.REGISTRATION)
    sent = True
    try:
        send_mail(
            subject="Your DristiSewa verification code",
            message=f"Your OTP code is {otp}. It expires in {expiry_minutes} minute(s).",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send OTP email to %s", email)
        sent = False
    return otp, sent


def branch_frontdesk_json(request, branch_id):
    """Public AJAX endpoint used on the registration page to list the
    Front Desk staff for a chosen branch, so a prospective student can
    pick who handles their application when a branch has more than one."""
    frontdesk_users = User.objects.filter(
        role=User.Role.FRONTDESK, branch_id=branch_id, is_active=True
    ).order_by("first_name", "last_name")

    return JsonResponse({
        "front_desk_staff": [
            {"id": fd.id, "name": fd.get_full_name() or fd.email}
            for fd in frontdesk_users
        ]
    })


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    from branches.models import Branch

    branches = Branch.objects.filter(is_active=True)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Stash registration details in the session until OTP is verified.
            request.session["pending_registration"] = {
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": data["email"],
                "phone": data.get("phone", ""),
                "branch_id": data["branch"].pk,
                "front_desk_user_id": data["front_desk_user"].pk if data.get("front_desk_user") else None,
                "password": data["password"],
            }
            request.session["email"] = data["email"]
            _, sent = _generate_and_send_otp(data["email"])
            if sent:
                messages.success(request, "An OTP has been sent to your email.")
            else:
                messages.error(
                    request,
                    "We couldn't send the OTP email right now. Please use Resend OTP, "
                    "or contact support if the problem continues.",
                )
            return redirect("accounts:verify_otp")
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return render(request, "registration/register.html", {"form": form, "branches": branches})

    return render(request, "registration/register.html", {"branches": branches})


def verify_otp(request):
    pending = request.session.get("pending_registration")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            otp = form.cleaned_data["otp"]

            record = OTPVerification.objects.filter(
                email=email, otp=otp, purpose=OTPVerification.Purpose.REGISTRATION, is_verified=False
            ).order_by("-created_at").first()

            if not record:
                messages.error(request, "Invalid OTP. Please try again.")
            elif record.is_expired():
                messages.error(request, "This OTP has expired. Please request a new one.")
            elif not pending or pending.get("email") != email:
                messages.error(request, "Your registration session has expired. Please register again.")
                return redirect("accounts:register")
            else:
                record.is_verified = True
                record.save(update_fields=["is_verified"])

                from branches.models import Branch

                branch = Branch.objects.filter(pk=pending.get("branch_id")).first()

                user = User.objects.create_user(
                    email=pending["email"],
                    password=pending["password"],
                    first_name=pending["first_name"],
                    last_name=pending["last_name"],
                    phone=pending.get("phone", ""),
                    role=User.Role.STUDENT,
                    branch=branch,
                )

                from students.models import Student

                # Assign the student to the chosen front desk user, or fall
                # back to the branch's sole front desk user (if it only has
                # one) so every student has an owner for follow-ups.
                assigned_to = None
                front_desk_user_id = pending.get("front_desk_user_id")
                if front_desk_user_id:
                    assigned_to = User.objects.filter(
                        pk=front_desk_user_id, role=User.Role.FRONTDESK, branch=branch
                    ).first()
                if not assigned_to and branch:
                    branch_frontdesk = User.objects.filter(
                        role=User.Role.FRONTDESK, branch=branch, is_active=True
                    )
                    if branch_frontdesk.count() == 1:
                        assigned_to = branch_frontdesk.first()

                Student.objects.get_or_create(user=user, defaults={"assigned_to": assigned_to})

                request.session.pop("pending_registration", None)
                request.session.pop("email", None)
                messages.success(request, "Your account has been verified successfully. Please log in to continue.")
                return redirect("accounts:login")

    return render(request, "registration/otp_verification.html")


def resend_otp(request):
    pending = request.session.get("pending_registration")
    email = request.session.get("email")

    if not pending or not email:
        messages.error(request, "Your registration session has expired. Please register again.")
        return redirect("accounts:register")

    _, sent = _generate_and_send_otp(email)
    if sent:
        messages.success(request, "A new OTP has been sent to your email.")
    else:
        messages.error(
            request,
            "We couldn't send the OTP email right now. Please try again in a moment.",
        )
    return redirect("accounts:verify_otp")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.role != User.Role.STUDENT and not user.is_superuser:
                    messages.error(request, "Staff accounts must use the staff login page.")
                else:
                    login(request, user)
                    return redirect("accounts:dashboard")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please enter a valid email and password.")

    return render(request, "registration/login.html")


def staff_login_view(request):
    """Shared login entry point for ADMIN, MANAGER, and FRONTDESK roles.

    The form includes a role dropdown; the selected role must match the
    account's actual role (admin accounts are created manually in the DB,
    managers create front desk accounts, etc.). Student accounts are
    rejected here and pointed to the student login page.
    """
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            selected_role = form.cleaned_data["role"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.role == User.Role.STUDENT:
                    messages.error(request, "Student accounts must use the student login page.")
                elif user.role != selected_role and not user.is_superuser:
                    messages.error(request, "Selected role does not match this account.")
                else:
                    login(request, user)
                    return redirect("accounts:dashboard")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Please fill in all fields correctly.")
    else:
        form = StaffLoginForm()

    return render(request, "registration/staff_login.html", {"form": form})


def logout_view(request):
    is_staff_user = request.user.is_authenticated and request.user.role in (
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.FRONTDESK,
    )
    logout(request)
    if is_staff_user:
        return redirect("accounts:staff_login")
    return redirect("accounts:home")


def dashboard_redirect(request):
    """Send an authenticated user to the dashboard for their role."""
    role = request.user.role
    mapping = {
        User.Role.ADMIN: "accounts:admin_dashboard",
        User.Role.MANAGER: "accounts:manager_dashboard",
        User.Role.FRONTDESK: "accounts:frontdesk_dashboard",
        User.Role.STUDENT: "accounts:student_dashboard",
    }
    return redirect(mapping.get(role, "accounts:home"))


def _student_growth_trend():
    """Percentage change in new student signups this month vs last month."""
    from datetime import timedelta

    from django.utils import timezone

    from students.models import Student

    today = timezone.localdate()
    this_month_count = Student.objects.filter(
        created_at__year=today.year, created_at__month=today.month
    ).count()

    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month_count = Student.objects.filter(
        created_at__year=last_month_date.year, created_at__month=last_month_date.month
    ).count()

    if last_month_count:
        return round(((this_month_count - last_month_count) / last_month_count) * 100, 1)
    return 100.0 if this_month_count else 0.0


@role_required("ADMIN")
def admin_dashboard(request):
    from branches.models import Branch
    from followups.models import FollowUp
    from students.models import Student

    try:
        from activity.models import ActivityLog

        recent_activity = ActivityLog.objects.select_related("user")[:5]
    except Exception:
        recent_activity = []

    active_branches = Branch.objects.filter(is_active=True)
    branch_counts = []
    for branch in active_branches:
        branch_counts.append((branch, Student.objects.filter(user__branch=branch).count()))
    max_count = max((count for _, count in branch_counts), default=0)

    branch_performance = []
    for branch, count in sorted(branch_counts, key=lambda item: item[1], reverse=True)[:5]:
        percent = round((count / max_count) * 100) if max_count else 0
        branch_performance.append({"name": branch.name, "count": count, "percent": percent})

    branch_staff_summary = []
    for branch in active_branches.order_by("name"):
        manager_count = User.objects.filter(branch=branch, role=User.Role.MANAGER).count()
        frontdesk_count = User.objects.filter(branch=branch, role=User.Role.FRONTDESK).count()
        branch_staff_summary.append(
            {
                "name": branch.name,
                "manager_count": manager_count,
                "frontdesk_count": frontdesk_count,
                "total_staff": manager_count + frontdesk_count,
            }
        )

    return render(
        request,
        "admin/overview.html",
        {
            "student_count": Student.objects.count(),
            "branch_count": active_branches.count(),
            "pending_followups": FollowUp.objects.filter(is_done=False).count(),
            "growth_trend": _student_growth_trend(),
            "branch_performance": branch_performance,
            "recent_activity": recent_activity,
            "branch_staff_summary": branch_staff_summary,
            "total_managers": User.objects.filter(role=User.Role.MANAGER).count(),
            "total_frontdesk": User.objects.filter(role=User.Role.FRONTDESK).count(),
        },
    )


@role_required("ADMIN")
def branch_staff(request):
    from branches.models import Branch
    from students.models import Student

    from .forms import AdminStaffForm

    edit_user_id = request.GET.get("edit_user", "")
    selected_branch = request.GET.get("branch", "").strip()

    if request.method == "POST" and "create_staff" in request.POST:
        form = AdminStaffForm(request.POST, require_password=True)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(email=data["email"]).exists():
                messages.error(request, f"A user with email {data['email']} already exists.")
            else:
                User.objects.create_user(
                    email=data["email"],
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data.get("last_name", ""),
                    role=data["role"],
                    branch=data.get("branch"),
                    experience_details=data.get("experience_details", ""),
                    is_staff=True,
                )
                messages.success(request, f"Account created for {data['email']}.")
                return redirect("accounts:branch_staff")
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    else:
        form = AdminStaffForm(require_password=True)

    user_edit_form = None
    if edit_user_id:
        target = User.objects.filter(
            pk=edit_user_id, role__in=[User.Role.MANAGER, User.Role.FRONTDESK]
        ).first()
        if target:
            user_edit_form = AdminStaffForm(
                initial={
                    "first_name": target.first_name,
                    "last_name": target.last_name,
                    "email": target.email,
                    "role": target.role,
                    "branch": target.branch_id,
                    "experience_details": target.experience_details,
                },
                require_password=False,
            )

    active_branches = Branch.objects.filter(is_active=True).order_by("name")

    branches_for_summary = active_branches
    if selected_branch:
        branches_for_summary = active_branches.filter(pk=selected_branch)

    branch_summary = []
    for branch in branches_for_summary:
        branch_managers = list(User.objects.filter(branch=branch, role=User.Role.MANAGER))
        branch_frontdesk = list(User.objects.filter(branch=branch, role=User.Role.FRONTDESK))
        manager_count = len(branch_managers)
        frontdesk_count = len(branch_frontdesk)
        student_count = Student.objects.filter(user__branch=branch).count()
        branch_summary.append(
            {
                "branch": branch,
                "managers": branch_managers,
                "frontdesk_staff": branch_frontdesk,
                "manager_count": manager_count,
                "frontdesk_count": frontdesk_count,
                "total_staff": manager_count + frontdesk_count,
                "student_count": student_count,
            }
        )

    if selected_branch:
        total_managers = sum(item["manager_count"] for item in branch_summary)
        total_frontdesk = sum(item["frontdesk_count"] for item in branch_summary)
    else:
        total_managers = User.objects.filter(role=User.Role.MANAGER).count()
        total_frontdesk = User.objects.filter(role=User.Role.FRONTDESK).count()

    return render(
        request,
        "admin/branch_staff.html",
        {
            "branches": active_branches,
            "selected_branch": selected_branch,
            "branch_summary": branch_summary,
            "branch_count": active_branches.count(),
            "total_managers": total_managers,
            "total_frontdesk": total_frontdesk,
            "form": form,
            "user_edit_form": user_edit_form,
            "edit_user_id": edit_user_id,
        },
    )


@role_required("ADMIN")
def create_staff_page(request):
    """Standalone full-page version of the staff creation form."""
    from .forms import AdminStaffForm

    if request.method == "POST":
        form = AdminStaffForm(request.POST, require_password=True)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(email=data["email"]).exists():
                messages.error(request, f"A user with email {data['email']} already exists.")
            else:
                User.objects.create_user(
                    email=data["email"],
                    password=data["password"],
                    first_name=data["first_name"],
                    last_name=data.get("last_name", ""),
                    role=data["role"],
                    branch=data.get("branch"),
                    experience_details=data.get("experience_details", ""),
                    is_staff=True,
                )
                messages.success(request, f"Account created for {data['email']}.")
                return redirect("accounts:branch_staff")
    else:
        form = AdminStaffForm(require_password=True)

    return render(request, "admin/create_staff.html", {"form": form})


@role_required("ADMIN")
def update_manager(request, user_id):
    from .forms import AdminStaffForm

    target = get_object_or_404(User, pk=user_id, role__in=[User.Role.MANAGER, User.Role.FRONTDESK])

    if request.method == "POST":
        form = AdminStaffForm(request.POST, require_password=False)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(email=data["email"]).exclude(pk=target.pk).exists():
                messages.error(request, f"A user with email {data['email']} already exists.")
                return redirect("accounts:branch_staff")

            target.first_name = data["first_name"]
            target.last_name = data.get("last_name", "")
            target.email = data["email"]
            target.role = data["role"]
            target.branch = data.get("branch")
            target.experience_details = data.get("experience_details", "")
            if data.get("password"):
                target.set_password(data["password"])
            target.save()
            messages.success(request, f"Updated account for {target.email}.")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

    return redirect("accounts:branch_staff")


@role_required("ADMIN")
def toggle_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.error(request, "You cannot change the status of your own account.")
    else:
        target.is_active = not target.is_active
        target.save(update_fields=["is_active"])
        messages.success(
            request, f"{target.email} is now {'active' if target.is_active else 'suspended'}."
        )
    return redirect("accounts:branch_staff")


@role_required("ADMIN")
def delete_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target == request.user:
        messages.error(request, "You cannot delete your own account.")
    else:
        email = target.email
        target.delete()
        messages.success(request, f"Removed account {email}.")
    return redirect("accounts:branch_staff")


@role_required("ADMIN")
def student_management(request):
    from datetime import timedelta

    from django.db.models import Q
    from django.utils import timezone

    from branches.models import Branch
    from students.models import Student

    students_qs = Student.objects.select_related("user", "user__branch").filter(is_archived=False)

    query = request.GET.get("q", "").strip()
    if query:
        students_qs = students_qs.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(user__phone__icontains=query)
        )

    branch_id = request.GET.get("branch", "").strip()
    if branch_id:
        students_qs = students_qs.filter(user__branch_id=branch_id)

    today = timezone.localdate()
    students_data = []
    for student in students_qs.order_by("user__first_name", "user__last_name").distinct():
        next_followup = student.followups.filter(is_done=False).order_by("scheduled_date").first()
        if next_followup and next_followup.scheduled_date:
            if next_followup.scheduled_date < today:
                follow_up_status = "due"
            elif next_followup.scheduled_date <= today + timedelta(days=7):
                follow_up_status = "upcoming"
            else:
                follow_up_status = "completed"
        else:
            follow_up_status = "completed"

        students_data.append(
            {
                "user": student.user,
                "phone_number": student.user.phone or "—",
                "is_active": student.user.is_active,
                "follow_up_status": follow_up_status,
            }
        )

    return render(
        request,
        "admin/student_management.html",
        {
            "students": students_data,
            "total_students": Student.objects.filter(is_archived=False).count(),
            "branches": Branch.objects.filter(is_active=True),
            "selected_branch": branch_id,
            "query": query,
        },
    )


@role_required("ADMIN")
def admin_documents(request):
    """View all student documents (PDF/JPEG/DOCS) across all branches."""
    from django.db.models import Q

    from branches.models import Branch
    from documents.models import Document

    documents_qs = Document.objects.select_related(
        "student", "student__user", "student__user__branch"
    )

    query = request.GET.get("q", "").strip()
    if query:
        documents_qs = documents_qs.filter(
            Q(student__user__first_name__icontains=query)
            | Q(student__user__last_name__icontains=query)
            | Q(student__user__email__icontains=query)
        )

    branch_id = request.GET.get("branch", "").strip()
    if branch_id:
        documents_qs = documents_qs.filter(student__user__branch_id=branch_id)

    doc_type = request.GET.get("doc_type", "").strip()
    if doc_type:
        documents_qs = documents_qs.filter(doc_type=doc_type)

    status = request.GET.get("status", "").strip()
    if status:
        documents_qs = documents_qs.filter(status=status)

    return render(
        request,
        "admin/documents.html",
        {
            "documents": documents_qs.order_by("-created_at"),
            "branches": Branch.objects.filter(is_active=True),
            "doc_types": Document.DocType.choices,
            "doc_statuses": Document.Status.choices,
            "selected_branch": branch_id,
            "selected_doc_type": doc_type,
            "selected_status": status,
            "query": query,
            "total_documents": Document.objects.count(),
        },
    )


@role_required("FRONTDESK")
def frontdesk_dashboard(request):
    from django.db.models import Q

    from core.services import filter_by_branch
    from documents.models import Document
    from followups.models import FollowUp
    from reports.services import dashboard_summary
    from students.models import Student

    base_students = Student.objects.select_related("user", "user__branch").filter(is_archived=False)
    base_students = filter_by_branch(request.user, base_students, branch_field="user__branch")

    # Counts for the summary cards are derived from the same active,
    # branch-scoped queryset that backs the table, so the numbers always
    # agree with what's actually listed below.
    total_students = base_students.count()
    pending_documents = Document.objects.filter(
        student__in=base_students, status=Document.Status.PENDING
    ).count()
    pending_followups = FollowUp.objects.filter(
        student__in=base_students, is_done=False
    ).count()

    students = base_students

    query = request.GET.get("q", "").strip()
    if query:
        terms = query.split()
        name_query = Q()
        for term in terms:
            name_query &= (
                Q(user__first_name__icontains=term)
                | Q(user__last_name__icontains=term)
            )
        students = students.filter(
            name_query
            | Q(user__email__icontains=query)
            | Q(user__phone__icontains=query)
        )

    test_type = request.GET.get("test_type", "").strip()
    if test_type:
        students = students.filter(test_type=test_type)

    sort = request.GET.get("sort", "name")
    sort_map = {
        "name": "user__first_name",
        "name_desc": "-user__first_name",
        "newest": "-created_at",
        "oldest": "created_at",
        "country": "preferred_country",
        "branch": "user__branch__name",
    }
    students = students.order_by(sort_map.get(sort, "user__first_name"))

    summary = dashboard_summary(request.user)
    summary["total_students"] = total_students
    summary["pending_documents"] = pending_documents
    summary["pending_followups"] = pending_followups

    return render(
        request,
        "dashboards/frontdesk_dashboard.html",
        {
            "summary": summary,
            "students": students.distinct(),
            "total_students": total_students,
            "query": query,
            "test_type": test_type,
            "test_types": Student.Test.choices,
            "sort": sort,
        },
    )


@role_required("STUDENT")
def student_dashboard(request):
    from students.forms import StudentProfileForm
    from students.models import Student

    student, _ = Student.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your details have been saved.")
            return redirect("documents:upload_docs")
        messages.error(request, "Please correct the errors below and try again.")
    else:
        form = StudentProfileForm(instance=student)

    return render(request, "dashboards/student_dashboard.html", {"student": student, "form": form})


@role_required("MANAGER")
def manager_dashboard(request):
    return redirect("accounts:branch_monitoring")


@role_required("MANAGER")
def branch_monitoring(request):
    from followups.models import FollowUp
    from students.models import Student

    user_branch = request.user.branch
    students = Student.objects.select_related("user", "user__branch", "assigned_to").prefetch_related(
        "applications", "documents"
    ).filter(is_archived=False, user__branch=user_branch)

    pending_trackers = FollowUp.objects.filter(
        student__user__branch=user_branch, is_done=False
    ).count()
    completed_trackers = FollowUp.objects.filter(
        student__user__branch=user_branch, is_done=True
    ).count()

    front_desk_staff = []
    if user_branch is not None:
        frontdesk_users = User.objects.filter(branch=user_branch, role=User.Role.FRONTDESK)
        for staff_user in frontdesk_users:
            assigned_students = Student.objects.filter(
                assigned_to=staff_user, user__branch=user_branch
            )
            staff_students = assigned_students.count()
            verified = assigned_students.filter(is_verified=True).count()
            pending = FollowUp.objects.filter(
                assigned_to=staff_user, student__user__branch=user_branch, is_done=False
            ).count()
            completed = FollowUp.objects.filter(
                assigned_to=staff_user, student__user__branch=user_branch, is_done=True
            ).count()
            front_desk_staff.append(
                {
                    "name": staff_user.get_full_name() or staff_user.email,
                    "email": staff_user.email,
                    "profile_pic": staff_user.profile_pic.url if staff_user.profile_pic else "",
                    "students": staff_students,
                    "verified": verified,
                    "pending": pending,
                    "completed": completed,
                    "status": "Active" if staff_user.is_online else "Inactive",
                }
            )

    branch_students = []
    for student in students.filter(assigned_to__isnull=False).order_by("user__first_name", "user__last_name"):
        tracking_status = "completed" if student.is_verified else "pending"
        documents = list(student.documents.all())
        latest_document = documents[0] if documents else None
        if latest_document:
            document_label = latest_document.get_doc_type_display()
            if len(documents) > 1:
                document_label += f" (+{len(documents) - 1} more)"
        else:
            document_label = "No documents"
        branch_students.append(
            {
                "id": student.id,
                "name": student.user.get_full_name() or student.user.email,
                "email": student.user.email,
                "phone": student.user.phone or "—",
                "assigned_by": student.assigned_to.get_full_name() if student.assigned_to else "Unassigned",
                "country": student.preferred_country or "N/A",
                "tracking": tracking_status,
                "document_label": document_label,
            }
        )

    total_students_count = students.count()
    assigned_students_count = len(branch_students)

    return render(
        request,
        "manager/branch_monitoring.html",
        {
            "total_branch_students": total_students_count,
            "assigned_students_count": assigned_students_count,
            "unassigned_students_count": total_students_count - assigned_students_count,
            "pending_trackers": pending_trackers,
            "completed_trackers": completed_trackers,
            "front_desk_staff": front_desk_staff,
            "active_branch": user_branch.name if user_branch else "Unknown",
            "branch_students": branch_students,
        },
    )


@role_required("MANAGER")
def followup_management(request):
    from datetime import timedelta

    from django.utils import timezone

    from applications.models import Application
    from followups.models import FollowUp
    from students.models import Student

    user_branch = request.user.branch
    today = timezone.localdate()

    students_qs = (
        Student.objects.select_related("user", "assigned_to")
        .prefetch_related("applications", "followups")
        .filter(is_archived=False, user__branch=user_branch, assigned_to__isnull=False)
    )

    if request.method == "POST":
        student = get_object_or_404(students_qs, pk=request.POST.get("student_id"))
        new_status_label = request.POST.get("status", "").strip()
        status_value = dict((label, value) for value, label in Application.Status.choices).get(new_status_label)
        if status_value:
            application = student.applications.first()
            if application:
                application.status = status_value
                application.save(update_fields=["status"])
            else:
                Application.objects.create(student=student, status=status_value)
            messages.success(request, f"Application status updated for {student.user.get_full_name() or student.user.email}.")
        return redirect("accounts:followup_management")

    status_options = [label for _, label in Application.Status.choices]

    students_data = []
    for student in students_qs.order_by("user__first_name", "user__last_name"):
        next_followup = (
            student.followups.filter(is_done=False).order_by("scheduled_date").first()
        )
        if next_followup and next_followup.scheduled_date:
            due = next_followup.scheduled_date
            if due < today:
                date_label = "overdue"
            elif due == today:
                date_label = "today"
            elif due == today + timedelta(days=1):
                date_label = "upcoming"
            else:
                date_label = "normal"
            followup_display = due.strftime("%b %d, %Y")
        else:
            date_label = "normal"
            followup_display = "—"

        latest_application = student.applications.first()
        status_display = latest_application.get_status_display() if latest_application else "New"

        students_data.append(
            {
                "id": student.id,
                "name": student.user.get_full_name() or student.user.email,
                "email": student.user.email,
                "phone": student.user.phone or "—",
                "country": student.preferred_country or "N/A",
                "followup": followup_display,
                "date_label": date_label,
                "assigned_by": student.assigned_to.get_full_name() if student.assigned_to else "Unassigned",
                "status": status_display,
            }
        )

    pending_trackers = FollowUp.objects.filter(
        student__user__branch=user_branch, is_done=False
    ).count()
    completed_trackers = FollowUp.objects.filter(
        student__user__branch=user_branch, is_done=True
    ).count()

    return render(
        request,
        "manager/followup_management.html",
        {
            "students": students_data,
            "status_options": status_options,
            "total": len(students_data),
            "total_branch_students": students_qs.count(),
            "pending_trackers": pending_trackers,
            "completed_trackers": completed_trackers,
        },
    )


@role_required("MANAGER")
def front_desk(request):
    user_branch = request.user.branch

    if request.method == "POST":
        form_action = request.POST.get("form_action", "create")
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        staff_id = request.POST.get("staff_id")

        first_name, _, last_name = name.partition(" ")

        if form_action == "create":
            if not name or not email or not password:
                messages.error(request, "Name, email, and password are required.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, f"A user with email {email} already exists.")
            else:
                User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=User.Role.FRONTDESK,
                    branch=user_branch,
                    is_staff=True,
                )
                messages.success(request, f"Front desk account created for {name}.")

        elif form_action == "edit" and staff_id:
            staff_user = get_object_or_404(
                User, pk=staff_id, role=User.Role.FRONTDESK, branch=user_branch
            )
            if email and email != staff_user.email and User.objects.filter(email=email).exclude(pk=staff_user.pk).exists():
                messages.error(request, f"A user with email {email} already exists.")
            else:
                staff_user.first_name = first_name
                staff_user.last_name = last_name
                if email:
                    staff_user.email = email
                if password:
                    staff_user.set_password(password)
                staff_user.save()
                messages.success(request, f"Front desk account updated for {name}.")

        elif form_action == "delete" and staff_id:
            staff_user = get_object_or_404(
                User, pk=staff_id, role=User.Role.FRONTDESK, branch=user_branch
            )
            staff_name = staff_user.get_full_name() or staff_user.email
            staff_user.delete()
            messages.success(request, f"Removed front desk account for {staff_name}.")

        return redirect("accounts:front_desk")

    front_desk_staff = User.objects.filter(
        role=User.Role.FRONTDESK, branch=user_branch
    ).order_by("first_name", "last_name")

    return render(
        request,
        "manager/front_desk.html",
        {"front_desk_staff": front_desk_staff, "user_branch": user_branch},
    )


@role_required("MANAGER")
def reports(request):
    import calendar

    from django.db.models import Count
    from django.utils import timezone

    from applications.models import Application
    from students.models import Student

    user_branch = request.user.branch
    today = timezone.localdate()

    students_qs = Student.objects.filter(is_archived=False, user__branch=user_branch)
    applications_qs = Application.objects.filter(student__in=students_qs)

    # ---- Top metric cards -------------------------------------------------
    visa_granted_count = applications_qs.filter(status=Application.Status.VISA_GRANTED).count()
    rejected_count = applications_qs.filter(status=Application.Status.REJECTED).count()
    decided_count = visa_granted_count + rejected_count
    visa_success_rate = round((visa_granted_count / decided_count) * 100, 1) if decided_count else 0

    def month_bounds(offset):
        """Return (year, month) for `offset` months before the current month."""
        month_index = today.month - offset
        year = today.year
        while month_index <= 0:
            month_index += 12
            year -= 1
        return year, month_index

    this_year, this_month = month_bounds(0)
    last_year, last_month = month_bounds(1)

    new_apps_this_month = applications_qs.filter(
        created_at__year=this_year, created_at__month=this_month
    ).count()
    new_apps_last_month = applications_qs.filter(
        created_at__year=last_year, created_at__month=last_month
    ).count()
    new_apps_delta = new_apps_this_month - new_apps_last_month

    coes_received_count = applications_qs.filter(
        status__in=[Application.Status.COE_RECEIVED, Application.Status.VISA_GRANTED]
    ).count()

    total_applications_count = applications_qs.count()
    dropped_share = round((rejected_count / total_applications_count) * 100, 1) if total_applications_count else 0

    # ---- Monthly student intake (last 6 months) ---------------------------
    intake_data = []
    for offset in range(5, -1, -1):
        year, month = month_bounds(offset)
        count = students_qs.filter(created_at__year=year, created_at__month=month).count()
        intake_data.append({"label": calendar.month_abbr[month], "count": count})

    max_intake = max((m["count"] for m in intake_data), default=0)
    for m in intake_data:
        m["height_px"] = round((m["count"] / max_intake) * 280) if max_intake else 8
        m["height_px"] = max(m["height_px"], 8)

    # ---- Top destination shares -------------------------------------------
    top_destinations = (
        students_qs.exclude(preferred_country="")
        .values("preferred_country")
        .annotate(total=Count("id"))
        .order_by("-total")[:4]
    )

    # ---- Front desk executive performance index ---------------------------
    offer_or_beyond = [
        Application.Status.OFFER_LETTER_RECEIVED,
        Application.Status.COE_APPLIED,
        Application.Status.COE_RECEIVED,
        Application.Status.VISA_GRANTED,
    ]
    coe_or_beyond = [Application.Status.COE_RECEIVED, Application.Status.VISA_GRANTED]

    staff_performance = []
    if user_branch is not None:
        frontdesk_users = User.objects.filter(branch=user_branch, role=User.Role.FRONTDESK)
        for staff_user in frontdesk_users:
            staff_apps = applications_qs.filter(student__assigned_to=staff_user)
            assigned_cases = students_qs.filter(assigned_to=staff_user).count()
            offers_secured = staff_apps.filter(status__in=offer_or_beyond).count()
            coe_issued = staff_apps.filter(status__in=coe_or_beyond).count()
            visas_granted = staff_apps.filter(status=Application.Status.VISA_GRANTED).count()
            conversion = round((visas_granted / assigned_cases) * 100, 1) if assigned_cases else 0
            staff_performance.append(
                {
                    "name": staff_user.get_full_name() or staff_user.email,
                    "assigned_cases": assigned_cases,
                    "offers_secured": offers_secured,
                    "coe_issued": coe_issued,
                    "visas_granted": visas_granted,
                    "conversion": conversion,
                }
            )

    return render(
        request,
        "manager/reports.html",
        {
            "visa_success_rate": visa_success_rate,
            "decided_count": decided_count,
            "new_apps_this_month": new_apps_this_month,
            "new_apps_delta": new_apps_delta,
            "coes_received_count": coes_received_count,
            "rejected_count": rejected_count,
            "dropped_share": dropped_share,
            "intake_data": intake_data,
            "top_destinations": top_destinations,
            "staff_performance": staff_performance,
        },
    )


@role_required("MANAGER")
def pending_followups(request):
    from followups.models import FollowUp

    user_branch = request.user.branch

    followups = (
        FollowUp.objects.select_related("student__user")
        .filter(student__user__branch=user_branch, is_done=False)
        .order_by("scheduled_date")
    )

    students = []
    for f in followups:
        student = f.student
        students.append(
            {
                "id": student.id,
                "name": student.user.get_full_name() or student.user.email,
                "email": student.user.email,
                "phone": student.user.phone or "—",
                "followup": f.scheduled_date.strftime("%b %d, %Y") if f.scheduled_date else "—",
            }
        )

    return render(request, "manager/followups_pending.html", {"students": students})


@role_required("MANAGER")
def complete_followups(request):
    from followups.models import FollowUp

    user_branch = request.user.branch

    followups = (
        FollowUp.objects.select_related("student__user")
        .filter(student__user__branch=user_branch, is_done=True)
        .order_by("-scheduled_date")
    )

    students = []
    for f in followups:
        student = f.student
        students.append(
            {
                "id": student.id,
                "name": student.user.get_full_name() or student.user.email,
                "email": student.user.email,
                "phone": student.user.phone or "—",
                "followup": f.scheduled_date.strftime("%b %d, %Y") if f.scheduled_date else "—",
            }
        )

    return render(request, "manager/followups_complete.html", {"students": students})


@role_required("MANAGER")
def student_document(request, student_id):
    from core.services import filter_by_branch
    from students.models import Student

    student = get_object_or_404(
        filter_by_branch(
            request.user,
            Student.objects.select_related("user", "user__branch", "assigned_to"),
            branch_field="user__branch",
        ),
        pk=student_id,
    )

    documents = student.documents.all()
    followups = student.followups.all()

    student_context = {
        "id": student.id,
        "name": student.user.get_full_name() or student.user.email,
        "phone": student.user.phone or "—",
        "email": student.user.email,
        "country": student.preferred_country or "—",
        "status": "Verified" if student.is_verified else "Pending Verification",
        "assigned_by": student.assigned_to.get_full_name() if student.assigned_to else "Unassigned",
        "documents": documents,
        "remarks": [{"date": f.created_at.strftime("%d %b %Y"), "text": f.note} for f in followups],
    }

    return render(
        request,
        "manager/student_document.html",
        {"student": student_context, "back_url": reverse("accounts:branch_monitoring")},
    )


@role_required("MANAGER")
def student_remark(request, student_id):
    from core.services import filter_by_branch
    from followups.models import FollowUp
    from students.models import Student

    student = get_object_or_404(
        filter_by_branch(request.user, Student.objects.all(), branch_field="user__branch"),
        pk=student_id,
    )

    if request.method == "POST":
        note = request.POST.get("student_remark", "").strip()
        if note:
            FollowUp.objects.create(student=student, assigned_to=request.user, note=note)
            messages.success(request, "Remark added.")

    return redirect(f"{reverse('accounts:student_document', kwargs={'student_id': student.pk})}#remarks")


@role_required("MANAGER")
def manager_document_delete(request, student_id, document_id):
    from core.services import filter_by_branch
    from documents.models import Document
    from students.models import Student

    student = get_object_or_404(
        filter_by_branch(request.user, Student.objects.all(), branch_field="user__branch"),
        pk=student_id,
    )
    document = get_object_or_404(Document, pk=document_id, student=student)
    document.delete()
    messages.success(request, "Document deleted.")
    return redirect("accounts:student_document", student_id=student.pk)


@role_required("MANAGER")
def manager_document_toggle_verify(request, student_id, document_id):
    """Toggle a document's review status between Approved and Pending."""
    from core.services import filter_by_branch
    from documents.models import Document
    from students.models import Student

    student = get_object_or_404(
        filter_by_branch(request.user, Student.objects.all(), branch_field="user__branch"),
        pk=student_id,
    )
    document = get_object_or_404(Document, pk=document_id, student=student)

    if document.status == Document.Status.APPROVED:
        document.status = Document.Status.PENDING
    else:
        document.status = Document.Status.APPROVED
    document.save(update_fields=["status"])

    return redirect(f"{reverse('accounts:student_document', kwargs={'student_id': student.pk})}#documents")
