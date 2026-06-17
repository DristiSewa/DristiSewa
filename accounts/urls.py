from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("register/branches/<int:branch_id>/frontdesk/", views.branch_frontdesk_json, name="branch_frontdesk_json"),
    path("login/", views.login_view, name="login"),
    path("staff-login/", views.staff_login_view, name="staff_login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/branch-staff/", views.branch_staff, name="branch_staff"),
    path("admin-panel/staff/create/", views.create_staff_page, name="create_staff_page"),
    path("admin-panel/students/", views.student_management, name="student_management"),
    path("admin-panel/documents/", views.admin_documents, name="admin_documents"),
    path("admin-panel/staff/<int:user_id>/update/", views.update_manager, name="update_manager"),
    path("admin-panel/staff/<int:user_id>/toggle/", views.toggle_user, name="toggle_user"),
    path("admin-panel/staff/<int:user_id>/delete/", views.delete_user, name="delete_user"),
    path("dashboard/manager/", views.manager_dashboard, name="manager_dashboard"),
    path("dashboard/frontdesk/", views.frontdesk_dashboard, name="frontdesk_dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("manager/branch-monitoring/", views.branch_monitoring, name="branch_monitoring"),
    path("manager/followup-management/", views.followup_management, name="followup_management"),
    path("manager/front-desk/", views.front_desk, name="front_desk"),
    path("manager/reports/", views.reports, name="reports"),
    path("manager/followups/pending/", views.pending_followups, name="pending_followups"),
    path("manager/followups/completed/", views.complete_followups, name="complete_followups"),
    path("manager/student/<int:student_id>/documents/", views.student_document, name="student_document"),
    path("manager/student/<int:student_id>/remark/", views.student_remark, name="student_remark"),
    path("manager/student/<int:student_id>/documents/<int:document_id>/delete/", views.manager_document_delete, name="manager_document_delete"),
    path("manager/student/<int:student_id>/documents/<int:document_id>/toggle-verify/", views.manager_document_toggle_verify, name="manager_document_toggle_verify"),
]
