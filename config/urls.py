from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("superadmin/", include(("superadmin.urls", "superadmin"), namespace="superadmin")),
    path("", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("branches/", include(("branches.urls", "branches"), namespace="branches")),
    path("students/", include(("students.urls", "students"), namespace="students")),
    path("frontdesk/", include(("frontdesk.urls", "frontdesk"), namespace="frontdesk")),
    path("applications/", include(("applications.urls", "applications"), namespace="applications")),
    path("documents/", include(("documents.urls", "documents"), namespace="documents")),
    path("followups/", include(("followups.urls", "followups"), namespace="followups")),
    path("reports/", include(("reports.urls", "reports"), namespace="reports")),
    path("analytics/", include(("analytics.urls", "analytics"), namespace="analytics")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
