# DristiSewa — Master Audit & Completion Prompt

Paste this entire prompt into a new Claude session (with the DristiSewa folder mounted)
to get a full feature audit, integrity check, and completion roadmap.

---

## CONTEXT

You are working on **DristiSewa**, a Django-based Student Consultancy Management System
located at `/Users/rohitthapa/Desktop/Final_Project/DristiSewa`.

**Tech stack:** Django 5, SQLite, Tailwind CSS (CDN), Font Awesome 6.4, Vanilla JS,
Python 3.14.

**Auth model:** `accounts.User` — email-based login, role field:
`ADMIN | MANAGER | FRONTDESK | STUDENT`. Branch-scoped via FK `user.branch`.

**Apps:** accounts, branches, students, followups, frontdesk, applications,
documents, analytics, activity, superadmin, reports, core.

**Four stakeholder portals:**
| Role | Dashboard entry | URL prefix |
|------|----------------|------------|
| Admin | `accounts:admin_dashboard` | `/dashboard/admin/` |
| Manager | `accounts:branch_monitoring` | `/manager/` |
| Front Desk | `accounts:frontdesk_dashboard` | `/dashboard/frontdesk/` |
| Student | `accounts:student_dashboard` | `/dashboard/student/` |

**Locked templates (no redesign):**
`templates/admin/*`, `templates/manager/*`,
`templates/dashboards/frontdesk_dashboard.html`,
`templates/followups/followup_list.html`,
`templates/dashboards/archived_students.html`,
`templates/dashboards/student_profile.html`

---

## TASK 1 — FEATURE & INTEGRITY AUDIT

For each stakeholder below, read the relevant views, URLs, and templates, then
produce a checklist table with columns:

| Feature | View exists? | URL wired? | Template exists? | Data is real (no mock)? | Cross-role integrity OK? | Status |

Use ✅ / ⚠️ (partial) / ❌ (missing or broken) in each column.
Status = **Done / Partial / Missing / Broken**.

### 1.1 Admin
- Login (email+password, staff_login_view)
- OTP registration flow (register → verify_otp → resend_otp)
- Admin dashboard with real stats (student_count, branch_count, pending_followups, growth_trend, branch_performance, recent_activity)
- Branch management: create branch (AJAX via branches:create_branch_json), list/filter branches
- Branch summary cards: manager count, frontdesk count, student count per branch
- Manager table: search, sort, edit via drawer (openEditManagerDrawer → accounts:update_manager)
- Create staff account (accounts:create_staff_page → POST)
- Toggle user active/inactive (accounts:toggle_user)
- Delete user (accounts:delete_user)
- Student management: list all students, search, branch filter, status filter
- Student profile view
- Document management (accounts:admin_documents)
- Logout

### 1.2 Manager
- Login (staff_login_view)
- Branch monitoring dashboard: total students, active follow-ups, pending appointments, recent registrations, front-desk staff online status, growth trend
- Student list (branch-scoped), search, filter
- Student profile view (full detail)
- Verify / archive student
- Follow-up management: pending list, complete list, add follow-up, mark done
- Appointment list, update status, cancel
- Document view, approve/reject with remarks, delete, toggle verify
- Front Desk staff management: add/edit/remove front desk accounts, generate passwords
- Reports: branch-wise stats, date-range filter
- Online student form monitoring (verification status)
- Logout

### 1.3 Front Desk
- Login (staff_login_view)
- Dashboard: branch student list, pending follow-ups, appointments
- Register new student
- Edit student profile (academic, test score, preferred country)
- Archive / unarchive student
- Assign student to staff member
- Upload document (PDF/JPEG)
- Assign document to manager
- Schedule follow-up, add remark, mark complete
- Appointment list, update status, cancel
- Student profile detail view
- Add remark to student profile
- Update application pipeline status
- Logout

### 1.4 Student
- Self-registration (name, email, password)
- OTP email verification
- Login
- Password reset via OTP
- Application form: personal info, academic background, English proficiency (IELTS/PTE/TOEFL + score), preferred country, preferred university/location
- Document upload (PDF/JPEG), re-upload if rejected
- View document review status + remarks
- View application pipeline status
- View follow-up history (read-only)
- Logout

---

## TASK 2 — CROSS-STAKEHOLDER INTEGRITY CHECK

Verify these data flows work end-to-end (trace from model → view → template):

1. **Student registration → Front Desk sees student** — Student self-registers; does the front desk student list show them immediately (branch scoping correct)?
2. **Front Desk uploads document → Manager sees it** — Document FK chain: `Document.student.user.branch` matches manager's branch?
3. **Front Desk schedules follow-up → Manager follow-up list shows it** — `FollowUp.assigned_to` vs manager branch scoping in `followup_management` view?
4. **Manager marks follow-up done → Front Desk follow-up list reflects it** — `followup_list` view queries `is_done` correctly?
5. **Admin creates Manager account → Manager can log in immediately** — `is_active` set to True on creation? Password hashed correctly?
6. **Admin creates Branch → Manager branch select shows it** — `AdminStaffForm` branch queryset uses `Branch.objects.filter(is_active=True)`?
7. **Student uploads document → Student sees approval status** — Student dashboard/profile queries `Document.objects.filter(student__user=request.user)`?
8. **Manager archives student → Front Desk archived list shows them** — `is_archived` filter consistent across both views?
9. **OTP expiry enforced** — `OTPVerification.is_expired()` called in `verify_otp` view before accepting OTP?
10. **Branch scoping enforced for all Manager/FrontDesk views** — No view leaks data from other branches (check `filter_by_branch` / `user.branch` usage)?

For each: ✅ Works / ⚠️ Partial / ❌ Broken — plus one-line explanation of the issue if not ✅.

---

## TASK 3 — COMPLETION ROADMAP

Based on the audit findings, output a prioritised backlog:

```
Priority | Feature | File(s) to edit | What to do
HIGH     | ...     | ...             | ...
MEDIUM   | ...     | ...             | ...
LOW      | ...     | ...             | ...
```

Then ask: **"Should I start fixing these now, beginning with HIGH priority items?"**
If yes, work through each item in order:
1. Read the relevant view/template
2. Implement the fix (real Django querysets, no mock data)
3. Run `python3 -m py_compile <file>` after every `.py` change
4. Confirm fix with a one-line summary before moving to the next item

---

## CONSTRAINTS (always apply)

- Do NOT rename apps, folders, or delete files unless explicitly told.
- Do NOT redesign locked templates — only additive backend wiring.
- All querysets must be real — no hardcoded/mock data.
- Run `python3 -m py_compile` on every edited `.py` file.
- Keep all frontend in the existing Tailwind CDN + Font Awesome stack.
- Branch-scope all Manager and Front Desk queries via `request.user.branch`.

---

*End of master prompt — paste above the line into a new session to begin the audit.*
