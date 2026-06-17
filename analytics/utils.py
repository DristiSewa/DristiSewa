"""Utilities for activity logging throughout the application."""

from analytics.models import DetailedActivityLog


def log_user_action(request, action, description="", entity_type="", entity_id="",
                   changes=None, status="SUCCESS"):
    """
    Log a user action with request context.

    Usage:
        from analytics.utils import log_user_action

        log_user_action(
            request,
            DetailedActivityLog.Action.STUDENT_CREATE,
            description="Student John Doe created",
            entity_type="Student",
            entity_id=str(student.id)
        )
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    branch = request.user.branch if request.user.is_authenticated else None

    DetailedActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
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


def log_action(user, action, description="", entity_type="", entity_id="",
              branch=None, changes=None, status="SUCCESS"):
    """
    Log an action without request context (for background tasks, signals, etc).

    Usage:
        from analytics.utils import log_action
        from analytics.models import DetailedActivityLog

        log_action(
            user=user,
            action=DetailedActivityLog.Action.STUDENT_VERIFY,
            description="Student verified after document approval",
            entity_type="Student",
            entity_id=str(student.id),
            branch=student.user.branch
        )
    """
    DetailedActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
        branch=branch,
        changes=changes,
        status=status,
    )


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_activity_summary(branch=None, days=30):
    """
    Get a summary of activities for a given branch and time period.

    Returns:
        dict: Summary with action counts and recent activities
    """
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now()
    start_date = today - timedelta(days=days)

    activities = DetailedActivityLog.objects.filter(
        created_at__gte=start_date
    )

    if branch:
        activities = activities.filter(branch=branch)

    summary = {
        'total_actions': activities.count(),
        'successful_actions': activities.filter(status='SUCCESS').count(),
        'failed_actions': activities.filter(status='FAILED').count(),
        'pending_actions': activities.filter(status='PENDING').count(),
        'action_types': {},
        'recent_activities': activities[:10]
    }

    # Count by action type
    from django.db.models import Count
    action_counts = activities.values('action').annotate(count=Count('id'))
    for item in action_counts:
        summary['action_types'][item['action']] = item['count']

    return summary


def log_login(request):
    """Log user login activity."""
    from analytics.models import DetailedActivityLog
    log_user_action(
        request,
        DetailedActivityLog.Action.LOGIN,
        description=f"User {request.user.email} logged in",
    )


def log_logout(request):
    """Log user logout activity."""
    from analytics.models import DetailedActivityLog
    if request.user.is_authenticated:
        log_action(
            request.user,
            DetailedActivityLog.Action.LOGOUT,
            description=f"User {request.user.email} logged out",
            branch=request.user.branch,
        )


def log_bulk_action(request, action_type, count, entity_type, description=""):
    """Log a bulk action affecting multiple records."""
    from analytics.models import DetailedActivityLog
    log_user_action(
        request,
        DetailedActivityLog.Action.BULK_ACTION,
        description=f"{action_type}: {count} {entity_type} affected. {description}",
        entity_type=entity_type,
        entity_id=f"bulk_{action_type}",
    )


def log_error(request, error_type, error_message, entity_type="", entity_id=""):
    """Log system errors for debugging and audit purposes."""
    from analytics.models import DetailedActivityLog
    log_user_action(
        request,
        DetailedActivityLog.Action.SYSTEM_ERROR,
        description=f"Error: {error_message}",
        entity_type=entity_type,
        entity_id=entity_id,
        status="FAILED",
    )
