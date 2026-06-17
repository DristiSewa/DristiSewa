from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """Function-based view decorator restricting access by `request.user.role`.

    Usage:
        @role_required("ADMIN", "MANAGER")
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser or user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this page.")

        return _wrapped

    return decorator
