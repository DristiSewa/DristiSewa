from django.utils import timezone


class LastSeenMiddleware:
    """Stamps `User.last_seen` on every authenticated request so the manager
    dashboards can derive an Active/Inactive (online/offline) status for
    front desk staff without a separate presence service."""

    # Avoid a DB write on literally every request.
    UPDATE_INTERVAL_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            now = timezone.now()
            last_seen = user.last_seen
            if not last_seen or (now - last_seen).total_seconds() > self.UPDATE_INTERVAL_SECONDS:
                user.last_seen = now
                user.save(update_fields=["last_seen"])

        return self.get_response(request)
