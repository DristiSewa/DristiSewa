import json
from datetime import datetime, timedelta

from django.db.models import Count, Q, Sum, Avg, F
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import User
from accounts.permissions import role_required
from applications.models import Application
from branches.models import Branch
from documents.models import Document
from followups.models import FollowUp
from students.models import Student

from .models import (
    DetailedActivityLog,
    AggregatedAnalytics,
    SystemHealthMetrics,
    BranchPerformanceSnapshot,
    UserEngagementMetrics,
)


def log_activity(user, action, description="", entity_type="", entity_id="",
                 ip_address=None, user_agent="", branch=None, changes=None, status="SUCCESS"):
    """Helper to log detailed activity."""
    DetailedActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=user_agent,
        branch=branch,
        changes=changes,
        status=status,
    )


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@role_required("ADMIN")
def advanced_analytics(request):
    """Comprehensive analytics dashboard for super admins."""
    today = timezone.localdate()

    # Get all branches
    branches = Branch.objects.filter(is_active=True)
    branch_id = request.GET.get('branch', '')

    if branch_id:
        branches_qs = branches.filter(id=branch_id)
    else:
        branches_qs = branches

    # Get date range
    days = request.GET.get('days', '30')
    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 30

    start_date = today - timedelta(days=days)

    # Aggregate data across selected branches
    analytics_data = AggregatedAnalytics.objects.filter(
        branch__in=branches_qs,
        date__gte=start_date
    ).order_by('date')

    # Calculate totals
    total_students = Student.objects.filter(user__branch__in=branches_qs, is_archived=False).count()
    total_applications = Application.objects.filter(student__user__branch__in=branches_qs).count()
    total_documents = Document.objects.filter(student__user__branch__in=branches_qs).count()
    pending_followups = FollowUp.objects.filter(
        student__user__branch__in=branches_qs,
        is_done=False
    ).count()

    # Visa success rate
    decided_apps = Application.objects.filter(
        student__user__branch__in=branches_qs,
        status__in=[Application.Status.VISA_GRANTED, Application.Status.REJECTED]
    ).count()

    visa_granted = Application.objects.filter(
        student__user__branch__in=branches_qs,
        status=Application.Status.VISA_GRANTED
    ).count()

    visa_success_rate = round((visa_granted / decided_apps * 100), 1) if decided_apps else 0

    # Trend data — built directly from real records (daily buckets)
    from django.db.models.functions import TruncDate
    from core.models import TimeStampedModel

    # Determine bucket size: daily for ≤30 days, else weekly
    if days <= 30:
        date_list = [start_date + timedelta(days=i) for i in range(days + 1)]
    else:
        date_list = [start_date + timedelta(weeks=i) for i in range((days // 7) + 1)]

    # Students registered per bucket
    student_registrations = (
        Student.objects.filter(
            user__branch__in=branches_qs,
            created_at__date__gte=start_date,
        )
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
    )
    student_by_date = {item['day']: item['count'] for item in student_registrations}

    # Visa grants per bucket (use updated_at as proxy for grant date)
    visa_grants = (
        Application.objects.filter(
            student__user__branch__in=branches_qs,
            status=Application.Status.VISA_GRANTED,
            updated_at__date__gte=start_date,
        )
        .annotate(day=TruncDate('updated_at'))
        .values('day')
        .annotate(count=Count('id'))
    )
    visa_by_date = {item['day']: item['count'] for item in visa_grants}

    trend_labels = []
    student_trend = []
    visa_trend = []

    for d in date_list:
        trend_labels.append(d.strftime('%b %d'))
        student_trend.append(student_by_date.get(d, 0))
        visa_trend.append(visa_by_date.get(d, 0))

    application_trend = []  # kept for template compat

    # Branch comparison — batched into 3 queries instead of N*4
    _b_student_map = {
        row["user__branch_id"]: row["cnt"]
        for row in Student.objects.filter(user__branch__in=branches_qs, is_archived=False)
        .values("user__branch_id")
        .annotate(cnt=Count("id"))
    }
    _b_app_map = {
        row["student__user__branch_id"]: row
        for row in Application.objects.filter(student__user__branch__in=branches_qs)
        .values("student__user__branch_id")
        .annotate(
            total=Count("id"),
            visas=Count("id", filter=Q(status=Application.Status.VISA_GRANTED)),
            decided=Count(
                "id",
                filter=Q(status__in=[Application.Status.VISA_GRANTED, Application.Status.REJECTED]),
            ),
        )
    }
    branch_stats = []
    for branch in branches_qs.order_by("name"):
        bmap = _b_app_map.get(branch.pk, {})
        visa_granted = bmap.get("visas", 0)
        decided = bmap.get("decided", 0)
        branch_stats.append({
            "name": branch.name,
            "students": _b_student_map.get(branch.pk, 0),
            "applications": bmap.get("total", 0),
            "visas_granted": visa_granted,
            "visa_rate": round((visa_granted / decided * 100), 1) if decided else 0,
        })

    # Recent activity
    recent_activities = DetailedActivityLog.objects.filter(
        branch__in=branches_qs
    ).select_related('user', 'branch')[:20]

    # Document status breakdown — 1 query with conditional counts
    _doc_counts = Document.objects.filter(student__user__branch__in=branches_qs).aggregate(
        pending=Count("id", filter=Q(status=Document.Status.PENDING)),
        approved=Count("id", filter=Q(status=Document.Status.APPROVED)),
        rejected=Count("id", filter=Q(status=Document.Status.REJECTED)),
    )
    document_status = {
        "Pending": _doc_counts["pending"],
        "Approved": _doc_counts["approved"],
        "Rejected": _doc_counts["rejected"],
    }

    # Application status breakdown — 1 query with conditional counts
    _status_filters = {label: Count("id", filter=Q(status=val)) for val, label in Application.Status.choices}
    _app_counts = Application.objects.filter(student__user__branch__in=branches_qs).aggregate(**_status_filters)
    application_status = {label: _app_counts[label] for label in _app_counts}

    return render(request, 'analytics/advanced_dashboard.html', {
        'total_students': total_students,
        'total_applications': total_applications,
        'total_documents': total_documents,
        'pending_followups': pending_followups,
        'visa_success_rate': visa_success_rate,
        'trend_labels': json.dumps(trend_labels),
        'student_trend': json.dumps(student_trend),
        'application_trend': json.dumps(application_trend),
        'visa_trend': json.dumps(visa_trend),
        'branch_stats': branch_stats,
        'document_status': document_status,
        'document_status_json': json.dumps(document_status),
        'application_status': application_status,
        'application_status_json': json.dumps(application_status),
        'recent_activities': recent_activities,
        'branches': branches,
        'selected_branch': branch_id,
        'days': days,
    })


@role_required("ADMIN")
def activity_audit_log(request):
    """View complete audit trail of all actions."""
    activities = DetailedActivityLog.objects.select_related('user', 'branch')

    # Filters
    action = request.GET.get('action', '')
    user_id = request.GET.get('user', '')
    branch_id = request.GET.get('branch', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')

    if action:
        activities = activities.filter(action=action)

    if user_id:
        activities = activities.filter(user_id=user_id)

    if branch_id:
        activities = activities.filter(branch_id=branch_id)

    if status:
        activities = activities.filter(status=status)

    if search:
        activities = activities.filter(
            Q(description__icontains=search) |
            Q(entity_id__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )

    # Get unique values for filters
    action_choices = DetailedActivityLog.Action.choices
    users = User.objects.filter(activity_logs__isnull=False).distinct()
    branches = Branch.objects.filter(activity_logs__isnull=False).distinct()

    # Pagination
    page = request.GET.get('page', 1)
    per_page = 50
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1

    total_activities = activities.count()
    total_pages = (total_activities + per_page - 1) // per_page

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    activities = activities[start_idx:end_idx]

    return render(request, 'analytics/audit_log.html', {
        'activities': activities,
        'action_choices': action_choices,
        'users': users,
        'branches': branches,
        'selected_action': action,
        'selected_user': user_id,
        'selected_branch': branch_id,
        'selected_status': status,
        'search': search,
        'current_page': page,
        'total_pages': total_pages,
        'per_page': per_page,
        'total_activities': total_activities,
    })


@role_required("ADMIN")
def user_performance_analytics(request):
    """Analytics on individual user/staff performance."""
    today = timezone.localdate()
    days = request.GET.get('days', '30')
    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 30

    start_date = today - timedelta(days=days)

    # Get performance metrics
    staff_users = User.objects.filter(
        role__in=[User.Role.MANAGER, User.Role.FRONTDESK],
        is_active=True
    )

    # Batch all engagement metrics in 2 queries instead of 2N
    _metrics_map = {
        row["user_id"]: row
        for row in UserEngagementMetrics.objects.filter(
            user__in=staff_users, date__gte=start_date
        )
        .values("user_id")
        .annotate(
            total_logins=Sum("login_count"),
            total_actions=Sum("total_actions"),
            students_processed=Sum("students_processed"),
            documents_reviewed=Sum("documents_reviewed"),
            followups_completed=Sum("followups_completed"),
            avg_response_time=Avg("average_response_time_hours"),
        )
    }
    _activity_map = {
        row["user_id"]: row["cnt"]
        for row in DetailedActivityLog.objects.filter(
            user__in=staff_users, created_at__date__gte=start_date
        )
        .values("user_id")
        .annotate(cnt=Count("id"))
    }

    staff_performance = []
    for user in staff_users.order_by("first_name", "last_name"):
        m = _metrics_map.get(user.pk, {})
        actions = m.get("total_actions") or _activity_map.get(user.pk, 0)
        staff_performance.append({
            "user": user,
            "logins": m.get("total_logins") or 0,
            "actions": actions or 0,
            "students_processed": m.get("students_processed") or 0,
            "documents_reviewed": m.get("documents_reviewed") or 0,
            "followups_completed": m.get("followups_completed") or 0,
            "avg_response_time": round(m.get("avg_response_time") or 0, 1),
            "is_online": user.is_online,
        })

    # Sort by most active
    staff_performance.sort(key=lambda x: x['actions'], reverse=True)

    # Team-wide summary totals (computed here since Django has no built-in
    # "sum" template filter)
    team_summary = {
        'member_count': len(staff_performance),
        'total_logins': sum(s['logins'] for s in staff_performance),
        'total_actions': sum(s['actions'] for s in staff_performance),
        'total_students_processed': sum(s['students_processed'] for s in staff_performance),
        'total_documents_reviewed': sum(s['documents_reviewed'] for s in staff_performance),
        'total_followups_completed': sum(s['followups_completed'] for s in staff_performance),
        'online_count': sum(1 for s in staff_performance if s['is_online']),
    }
    response_times = [s['avg_response_time'] for s in staff_performance if s['avg_response_time']]
    team_summary['avg_response_time'] = round(sum(response_times) / len(response_times), 1) if response_times else 0

    # Highest action count, for normalizing progress bars
    max_actions = max((s['actions'] for s in staff_performance), default=0)
    for s in staff_performance:
        s['actions_percent'] = round((s['actions'] / max_actions) * 100, 1) if max_actions else 0

    most_active = staff_performance[0] if staff_performance else None
    top_performer = max(staff_performance, key=lambda x: x['students_processed'], default=None)
    fastest_response = min(
        (s for s in staff_performance if s['avg_response_time']),
        key=lambda x: x['avg_response_time'],
        default=None,
    )

    return render(request, 'analytics/user_performance.html', {
        'staff_performance': staff_performance,
        'team_summary': team_summary,
        'most_active': most_active,
        'top_performer': top_performer,
        'fastest_response': fastest_response,
        'days': days,
    })


@role_required("ADMIN")
@require_http_methods(["GET"])
def analytics_api(request):
    """JSON API endpoint for analytics data (for AJAX/frontend integration)."""
    metric = request.GET.get('metric', '')
    branch_id = request.GET.get('branch', '')
    days = request.GET.get('days', '30')

    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 30

    today = timezone.localdate()
    start_date = today - timedelta(days=days)

    data = {}

    if metric == 'student_growth':
        analytics = AggregatedAnalytics.objects.filter(
            date__gte=start_date
        ).order_by('date')

        if branch_id:
            analytics = analytics.filter(branch_id=branch_id)

        data = {
            'labels': [a.date.strftime('%b %d') for a in analytics],
            'values': [a.total_students for a in analytics],
        }

    elif metric == 'visa_success':
        analytics = AggregatedAnalytics.objects.filter(
            date__gte=start_date
        ).order_by('date')

        if branch_id:
            analytics = analytics.filter(branch_id=branch_id)

        data = {
            'labels': [a.date.strftime('%b %d') for a in analytics],
            'values': [a.visa_success_rate for a in analytics],
        }

    elif metric == 'application_status':
        branches_qs = Branch.objects.all()
        if branch_id:
            branches_qs = branches_qs.filter(id=branch_id)

        applications = Application.objects.filter(
            student__user__branch__in=branches_qs
        )

        data = {
            'Pending': applications.filter(status=Application.Status.PENDING).count(),
            'Approved': applications.filter(status=Application.Status.APPROVED).count(),
            'Rejected': applications.filter(status=Application.Status.REJECTED).count(),
            'Visa Granted': applications.filter(status=Application.Status.VISA_GRANTED).count(),
        }

    elif metric == 'document_status':
        branches_qs = Branch.objects.all()
        if branch_id:
            branches_qs = branches_qs.filter(id=branch_id)

        documents = Document.objects.filter(student__user__branch__in=branches_qs)

        data = {
            'Pending': documents.filter(status=Document.Status.PENDING).count(),
            'Approved': documents.filter(status=Document.Status.APPROVED).count(),
            'Rejected': documents.filter(status=Document.Status.REJECTED).count(),
        }

    return JsonResponse(data)


def generate_daily_analytics():
    """Task to generate daily aggregated analytics. Call this once per day."""
    from django.db.models import Count, Q

    today = timezone.localdate()

    for branch in Branch.objects.all():
        students = Student.objects.filter(user__branch=branch)

        analytics, _ = AggregatedAnalytics.objects.get_or_create(
            date=today,
            branch=branch,
            defaults={
                'total_students': students.count(),
                'new_students': students.filter(created_at__date=today).count(),
                'active_students': students.filter(user__is_active=True).count(),
                'verified_students': students.filter(is_verified=True).count(),
                'archived_students': students.filter(is_archived=True).count(),
            }
        )

        # Update application metrics
        applications = Application.objects.filter(student__user__branch=branch)
        analytics.total_applications = applications.count()
        analytics.applications_pending = applications.filter(
            status=Application.Status.PENDING
        ).count()
        analytics.applications_approved = applications.filter(
            status=Application.Status.APPROVED
        ).count()
        analytics.applications_rejected = applications.filter(
            status=Application.Status.REJECTED
        ).count()
        analytics.applications_visa_granted = applications.filter(
            status=Application.Status.VISA_GRANTED
        ).count()

        # Calculate visa success rate
        decided = analytics.applications_visa_granted + analytics.applications_rejected
        if decided > 0:
            analytics.visa_success_rate = round(
                (analytics.applications_visa_granted / decided) * 100, 1
            )

        # Document metrics
        documents = Document.objects.filter(student__user__branch=branch)
        analytics.total_documents = documents.count()
        analytics.documents_pending = documents.filter(
            status=Document.Status.PENDING
        ).count()
        analytics.documents_approved = documents.filter(
            status=Document.Status.APPROVED
        ).count()
        analytics.documents_rejected = documents.filter(
            status=Document.Status.REJECTED
        ).count()

        # Follow-up metrics
        followups = FollowUp.objects.filter(student__user__branch=branch)
        analytics.followups_pending = followups.filter(is_done=False).count()
        analytics.followups_completed = followups.filter(is_done=True).count()

        # Staff metrics
        analytics.total_managers = User.objects.filter(
            branch=branch,
            role=User.Role.MANAGER
        ).count()
        analytics.total_frontdesk = User.objects.filter(
            branch=branch,
            role=User.Role.FRONTDESK
        ).count()

        # Average documents per student
        if analytics.total_students > 0:
            analytics.avg_documents_per_student = round(
                analytics.total_documents / analytics.total_students, 2
            )

        analytics.save()
