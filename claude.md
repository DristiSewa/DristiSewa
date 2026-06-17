# DristiSewa — Project Notes for Claude

## Architecture
Django project, custom User model (accounts.User) with role field:
ADMIN, MANAGER, FRONTDESK, STUDENT. Branch-scoped via core.services.filter_by_branch.

## Locked frontend templates (DO NOT redesign)
The following templates must visually match the original DristiSewa*<Role> 
reference HTML (light theme, Tailwind CDN, Font Awesome 6.0.0, Inter font,
indigo sidebar #3f39c5, bg #f4f7fe). Only additive backend wiring 
(URL names, context vars, form actions) is allowed — no new layouts:
- templates/dashboards/frontdesk_dashboard.html
- templates/followups/followup_list.html
- templates/dashboards/archived_students.html
- templates/dashboards/student_profile.html

## Manager role — REWORKED (DONE)
The fabricated dark "luxury-glass-card" templates/dashboards/manager_dashboard.html
has been removed. accounts.views.manager_dashboard now redirects to
accounts:branch_monitoring. The real manager UI lives in templates/manager/
(base.html + branch_monitoring.html, followup_management.html, front_desk.html,
reports.html, student_document.html, followups_pending.html,
followups_complete.html), ported from the DristiSewaManager reference
(light theme, --primary #2b35d2, Inter font, Font Awesome 6.4.0).
Treat templates/manager/* as locked in the same way as the frontdesk templates
— only additive backend wiring, no redesign.

## Admin role — REWORKED (DONE)
The fabricated dark "luxury-glass-card" templates/dashboards/admin_dashboard.html
has been removed (no longer referenced anywhere). The real admin UI lives in
templates/admin/ (base.html + overview.html, branch_staff.html,
student_management.html), ported from the DristiSewaAdmin reference
(light theme, Tailwind CDN, blue-600 sidebar, Font Awesome 6.4.0).
accounts.views.admin_dashboard renders admin/overview.html with real stats
(student_count, branch_count, pending_followups, growth_trend,
branch_performance, recent_activity from activity.ActivityLog).
New routes: accounts:branch_staff, accounts:student_management,
accounts:update_manager, accounts:toggle_user, accounts:delete_user, and
branches:create_branch_json (AJAX quick-create branch from the staff drawer).
Admin "Branch & Staff" lists/edits accounts.User accounts with
role=MANAGER/FRONTDESK (added accounts.User.experience_details TextField,
migration 0003). Treat templates/admin/* as locked in the same way as the
frontdesk/manager templates — only additive backend wiring, no redesign.

## Rules
- Do not rename apps/folders, do not delete files unless explicitly told.
- Backend: real Django querysets, no mock data.
- Run `python3 -m py_compile` on edited .py files before calling a task done.