# DristiSewa Advanced Analytics System

## Overview

The Analytics system provides comprehensive insights into your consultancy operations with real-time dashboards, complete audit trails, and detailed performance metrics. The system creates a **superadmin database** that centralizes all records across all branches.

## Key Features

### 1. **Advanced Analytics Dashboard** (`/analytics/advanced/`)
- **Real-time Charts & Graphs**: Visual representations of student growth, application trends, visa success rates
- **Branch Comparison**: Performance metrics across all branches
- **Document & Application Status**: Breakdown of document and application statuses
- **Recent Activity Feed**: Latest system actions at a glance
- **Time Period Filtering**: View data from 7, 30, 90, or 365 days

**Key Metrics Displayed:**
- Total Students
- Total Applications
- Visa Success Rate
- Pending Follow-ups
- Student Growth Trends
- Branch Performance Rankings
- Document Processing Status
- Application Status Distribution

### 2. **Complete Audit Log** (`/analytics/audit-log/`)
- **Detailed Action Logging**: Every action in the system is recorded with:
  - Action type (login, document upload, application update, etc.)
  - User who performed the action
  - Branch involved
  - Timestamp
  - IP address and user agent
  - Success/failure status
  - Detailed change information (what changed)

- **Advanced Filtering:**
  - By action type
  - By user
  - By branch
  - By status (success/failed/pending)
  - Text search across all descriptions

- **Pagination**: View 50 records per page with navigation controls

### 3. **User Performance Analytics** (`/analytics/user-performance/`)
- **Individual Staff Metrics:**
  - Login frequency
  - Total actions performed
  - Students processed
  - Documents reviewed
  - Follow-ups completed
  - Average response time

- **Team Summary**: Aggregate statistics for the entire team
- **Performance Insights**: Top performers, most active staff, best response times
- **Online Status**: Real-time indication of who is currently active
- **Time Period Analysis**: View 7, 30, 90, or 365 days of performance data

## Database Models

### 1. **DetailedActivityLog** (Complete Audit Trail)
Stores comprehensive records of all system actions:

```python
- user: ForeignKey to User
- action: Choice field (LOGIN, LOGOUT, USER_CREATE, USER_UPDATE, etc.)
- branch: ForeignKey to Branch
- description: Detailed description of what happened
- entity_type: What was affected (Student, Document, Application, etc.)
- entity_id: ID of affected entity
- ip_address: Client IP address
- user_agent: Browser/client information
- status: SUCCESS, FAILED, or PENDING
- changes: JSON field with before/after data
- created_at: Timestamp
```

### 2. **AggregatedAnalytics** (Daily Metrics Snapshot)
Pre-calculated daily metrics for fast dashboard access:

```python
- date: DateField (daily snapshot)
- branch: ForeignKey to Branch
- total_students, new_students, active_students, verified_students
- total_applications, applications_pending, applications_approved, etc.
- visa_success_rate, student_growth_percentage
- total_documents, followups_pending, followups_completed
- total_managers, total_frontdesk
- avg_documents_per_student
```

### 3. **SystemHealthMetrics** (System Performance)
Tracks system health and performance:

```python
- timestamp: When measurement was taken
- database_size_mb: Database file size
- query_time_ms: Average query execution time
- request_count_hourly: Requests in the last hour
- error_count_hourly: Errors in the last hour
- cpu_usage_percent, memory_usage_percent, disk_usage_percent
- cache_hit_rate: Cache effectiveness
- status: HEALTHY, DEGRADED, or CRITICAL
```

### 4. **BranchPerformanceSnapshot** (Monthly Branch Analysis)
Monthly aggregated data for branch-to-branch comparison:

```python
- month: First day of the month
- branch: ForeignKey to Branch
- total_students_month_end, new_enrollments
- applications_submitted, visas_granted, visa_success_rate
- avg_days_to_visa, document_approval_rate
- avg_students_per_staff
- rank_among_branches: Ranking among all branches
```

### 5. **UserEngagementMetrics** (Staff Activity Tracking)
Daily engagement metrics for each staff member:

```python
- date: Day of activity
- user: Staff member
- branch: Their branch
- login_count: How many times they logged in
- active_sessions: Concurrent sessions
- total_actions: Total actions performed
- students_processed, documents_reviewed, followups_completed
- average_response_time_hours: Avg response speed
- error_rate: Percentage of failed actions
```

## How It Works

### Automatic Logging
The system automatically captures actions through Django signals:

1. **Student Actions**: Creation, updates, verification
2. **Application Actions**: Status changes, submissions
3. **Document Actions**: Uploads, approvals, rejections
4. **Follow-up Actions**: Creation, completion
5. **User Actions**: Login, logout, account changes

### Daily Analytics Generation
Run this command daily (via cron job or task scheduler) to generate aggregated metrics:

```bash
python manage.py generate_daily_analytics
```

This command:
1. Calculates metrics for each branch
2. Stores in `AggregatedAnalytics` table
3. Pre-computes complex calculations for faster dashboard loading
4. Maintains historical data for trend analysis

### Real-time Activity Logging
Every action is captured in `DetailedActivityLog` in real-time through:
1. Django signals (automatic)
2. Manual logging via `log_activity()` helper function

## API Endpoints

### JSON API for Frontend Integration
`GET /analytics/api/`

Query parameters:
- `metric`: Type of metric (student_growth, visa_success, application_status, document_status)
- `branch`: Optional branch ID
- `days`: Time period (default: 30)

Examples:
```
/analytics/api/?metric=student_growth&days=7
/analytics/api/?metric=visa_success&branch=1
/analytics/api/?metric=application_status
```

Returns JSON data suitable for charting libraries like Chart.js.

## Access Control

All analytics pages are protected with `@role_required("ADMIN")` decorator. Only admin users can:
- View advanced analytics dashboard
- Access complete audit logs
- View all user performance data
- Filter across all branches

## Integration with Django Admin

The analytics models are fully integrated with Django's admin interface:

1. **DetailedActivityLog Admin**: Color-coded by action type and status
2. **AggregatedAnalytics Admin**: Organized by date and branch
3. **SystemHealthMetrics Admin**: Status indicators (Healthy/Degraded/Critical)
4. **BranchPerformanceSnapshot Admin**: Monthly rankings and comparisons
5. **UserEngagementMetrics Admin**: Staff activity summaries

Access at `/admin/analytics/`

## Configuration

### Signals (Auto-logging)
Edit `analytics/signals.py` to add more auto-logged actions for your specific needs.

### Activity Log Actions
Add new action types to `DetailedActivityLog.Action` choices:

```python
class Action(models.TextChoices):
    YOUR_ACTION = "YOUR_ACTION", "Display Name"
```

### Daily Analytics Task
Schedule the `generate_daily_analytics` command using:
- **Linux/Mac**: Cron job
  ```bash
  0 1 * * * cd /path/to/project && python manage.py generate_daily_analytics
  ```
- **Windows**: Task Scheduler
- **Cloud**: Cloud tasks or functions (e.g., AWS Lambda, Cloud Functions)

## Usage Examples

### View Advanced Analytics for a Specific Branch
1. Go to `/analytics/advanced/`
2. Select branch from dropdown
3. Choose time period (7, 30, 90, or 365 days)
4. Click "Update"

### Search Audit Log for User Activities
1. Go to `/analytics/audit-log/`
2. Select user from "User" dropdown
3. Optionally filter by action type, branch, status
4. Use search box for keyword matching
5. Browse pages of results

### Monitor Staff Performance
1. Go to `/analytics/user-performance/`
2. Select time period (7, 30, 90, or 365 days)
3. View individual performance cards
4. Check "Most Active", "Top Performer", "Best Response Time" insights

## Best Practices

1. **Regular Analytics Generation**: Schedule daily generation for best performance
2. **Archive Old Data**: Consider archiving audit logs older than 1 year to keep DB size manageable
3. **Monitor System Health**: Regularly check SystemHealthMetrics for issues
4. **Review Audit Logs**: Periodically review audit logs for security and compliance
5. **Branch Comparison**: Use monthly snapshots for branch performance reviews

## Performance Optimization

1. **Indexed Fields**: All critical fields are indexed for fast queries
2. **Aggregation**: Daily snapshots prevent need to recalculate from raw data
3. **Pagination**: Audit log uses pagination to limit data transfer
4. **Query Optimization**: Uses `select_related()` and `prefetch_related()` where possible

## Future Enhancements

Potential features to add:
- Machine learning predictions (visa success prediction)
- Anomaly detection (unusual activity patterns)
- Custom report builder
- Email notifications for critical metrics
- Data export to Excel/PDF
- Integration with external BI tools
- Predictive analytics for staff workload
- Student success rate predictions

## Troubleshooting

### Analytics Not Updating
- Check if `generate_daily_analytics` command is running
- Check Django logs for errors
- Ensure background tasks/cron jobs are properly configured

### Slow Dashboard Loading
- Run `generate_daily_analytics` to populate `AggregatedAnalytics`
- Check if database indexes are properly created
- Consider archiving old audit logs

### Missing Activity Data
- Check if signals are properly imported in `apps.py`
- Verify `analytics` app is in `INSTALLED_APPS`
- Check Django admin interface for logged activities

## Support

For questions or issues, check:
1. Django admin interface at `/admin/analytics/`
2. Database logs in Django's logging system
3. System health metrics dashboard

---

**Last Updated**: June 2026
**Version**: 1.0
