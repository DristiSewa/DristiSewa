from django.shortcuts import render

from accounts.permissions import role_required
from .services import dashboard_summary


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def overview(request):
    return render(request, "reports/overview.html", {"summary": dashboard_summary(request.user)})
