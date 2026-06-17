from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Class-based view mixin that restricts access to users whose `role`
    attribute is in `allowed_roles`. Superusers always pass.

    Usage:
        class MyView(RoleRequiredMixin, ListView):
            allowed_roles = ["ADMIN", "MANAGER"]
    """

    allowed_roles: list[str] = []

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You do not have permission to access this page.")


class BranchScopedQuerysetMixin:
    """Mixin for ListViews/DetailViews that scopes `get_queryset()` to the
    current user's branch via `core.services.filter_by_branch`."""

    branch_field = "branch"

    def get_queryset(self):
        from core.services import filter_by_branch

        qs = super().get_queryset()
        return filter_by_branch(self.request.user, qs, branch_field=self.branch_field)
