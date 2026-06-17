"""Middleware for analytics data collection."""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from analytics.utils import log_login, log_logout


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Automatically log user login."""
    try:
        log_login(request)
    except Exception:
        pass  # Don't break login if logging fails


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Automatically log user logout."""
    try:
        log_logout(request)
    except Exception:
        pass  # Don't break logout if logging fails
