"""Shared query helpers used across apps for branch-scoped (multi-tenant) data access."""


def filter_by_branch(user, queryset, branch_field="branch"):
    """
    Restrict a queryset to the requesting user's branch.

    - ADMIN and MANAGER roles see every record (cross-branch oversight).
    - FRONTDESK / STUDENT (and any other role) only see records belonging
      to their own branch. If the user has no branch assigned, they see
      nothing (rather than leaking cross-branch data).
    """
    if not getattr(user, "is_authenticated", False):
        return queryset.none()

    role = getattr(user, "role", None)
    if role in ("ADMIN", "MANAGER") or getattr(user, "is_superuser", False):
        return queryset

    branch = getattr(user, "branch", None)
    if branch is None:
        return queryset.none()

    return queryset.filter(**{branch_field: branch})


def pipeline_counts(queryset, status_field="status", choices=None):
    """Return an ordered dict of {status_label: count} for a queryset, useful for
    funnel/pipeline reporting dashboards."""
    from collections import OrderedDict

    counts = OrderedDict()
    if choices is None:
        choices = queryset.model._meta.get_field(status_field).choices or []

    for value, label in choices:
        counts[label] = queryset.filter(**{status_field: value}).count()
    return counts
