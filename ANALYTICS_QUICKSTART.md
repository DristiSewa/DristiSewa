# Analytics System - Quick Start Guide

## ⚡ 5-Minute Setup

Your analytics system is **already installed and ready to use!** Here's how to start:

### Step 1: View the Analytics Dashboard
1. Log in as an Admin user
2. Navigate to the Admin Dashboard (homepage after login)
3. Scroll down to see **"Advanced Analytics & Audit Tools"** section
4. Click **"Advanced Analytics"** to open the dashboard

### Step 2: Set Up Daily Analytics (Optional but Recommended)
To populate analytics with data from your operations:

**Option A: Run Manually (for testing)**
```bash
python manage.py generate_daily_analytics
```

**Option B: Schedule Automatically (Production)**

**Linux/Mac:**
```bash
# Open your crontab
crontab -e

# Add this line (runs daily at 1:00 AM)
0 1 * * * cd /path/to/DristiSewa && python manage.py generate_daily_analytics
```

**Windows:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily, 1:00 AM
4. Set action: `python manage.py generate_daily_analytics`
5. Set working directory: `/path/to/DristiSewa`

### Step 3: Access All Analytics Pages

From the Admin Dashboard, you can access:

**1. Advanced Analytics** (`/analytics/advanced/`)
- Real-time charts and metrics
- Student growth trends
- Application status distribution
- Document statistics
- Branch performance comparison
- Recent activity feed

**2. Activity Audit Log** (`/analytics/audit-log/`)
- Complete history of all system actions
- Filter by user, branch, action type, status
- Search by keywords
- Pagination for easy browsing
- Perfect for security audits and compliance

**3. User Performance** (`/analytics/user-performance/`)
- Individual staff productivity metrics
- Login counts and action history
- Students processed, documents reviewed
- Response time tracking
- Team summary and insights

---

## 📊 What's Being Tracked Automatically

The system automatically logs:

✅ **User Activities**
- Login/logout
- Account creation/deletion
- Permission changes

✅ **Student Management**
- Student enrollment
- Student verification
- Student archival

✅ **Applications**
- Application creation
- Status updates (pending → approved → visa granted, etc.)

✅ **Documents**
- Document uploads
- Approvals/rejections
- Deletions

✅ **Follow-ups**
- Follow-up creation
- Follow-up completion

✅ **System Actions**
- Errors and failures
- Bulk operations
- Data exports

---

## 🎯 Common Use Cases

### Use Case 1: Check Branch Performance
1. Go to `/analytics/advanced/`
2. Select your branch from dropdown
3. Choose time period (Last 30 Days, etc.)
4. View charts and metrics instantly

### Use Case 2: Find Who Did What
1. Go to `/analytics/audit-log/`
2. Use filters to search:
   - **By action**: e.g., "DOCUMENT_UPLOAD"
   - **By user**: e.g., "John Manager"
   - **By branch**: e.g., "Kathmandu"
   - **By date**: Automatically shows newest first
3. Use search box for keywords

### Use Case 3: Evaluate Staff Performance
1. Go to `/analytics/user-performance/`
2. Select time period (7, 30, 90, or 365 days)
3. View individual cards for each staff member:
   - Logins and actions
   - Students processed
   - Documents reviewed
   - Response time
4. Check "Performance Insights" section for:
   - Most active staff
   - Top performer
   - Best response time

### Use Case 4: Track a Student's Journey
1. Go to `/analytics/audit-log/`
2. Search for student's email or name
3. See timeline of all actions related to that student:
   - When enrolled
   - When verified
   - When documents uploaded
   - When application status changed
   - When follow-ups created

### Use Case 5: Security Audit
1. Go to `/analytics/audit-log/`
2. Filter by status "FAILED"
3. Review all failed attempts
4. Check IP addresses for suspicious activity
5. View user agent info to identify device

---

## 🔍 Understanding the Dashboard

### Advanced Analytics Dashboard

**Top Metrics Cards** (Blue, Green, Orange, Pink):
- Total Students: All enrolled students
- Total Applications: All submitted applications
- Visa Success Rate: % of applications that got visa
- Pending Follow-ups: Actions that need completion

**Line Chart - Student Trend**:
- Shows how your student count grows over time
- Helps identify growth rate and trends

**Doughnut Chart - Application Status**:
- Visual distribution of applications
- Pending, Approved, Rejected, Visa Granted

**Bar Chart - Document Status**:
- Count of documents by status
- Pending, Approved, Rejected

**Area Chart - Visa Grants**:
- How many visas approved over time
- Shows success frequency

**Branch Performance Cards**:
- Each branch shown with:
  - Student count
  - Application count
  - Visas granted
  - Success rate percentage

**Recent Activity Feed**:
- Latest 20 system actions
- Shows what's happening in real-time

---

## 🔧 Adding Custom Logging (Advanced)

If you want to log custom actions in your code:

```python
from analytics.utils import log_user_action
from analytics.models import DetailedActivityLog

# In a view function:
def my_custom_action(request):
    # ... do something ...
    
    log_user_action(
        request,
        DetailedActivityLog.Action.BULK_ACTION,
        description="Sent acceptance letter to 5 students",
        entity_type="Student",
        entity_id="batch_001"
    )
    
    return response
```

---

## 🚨 Troubleshooting

**Q: Analytics page shows "No data available"**
- A: Run `python manage.py generate_daily_analytics` to populate initial data

**Q: Dashboard loading slowly**
- A: Make sure `generate_daily_analytics` runs daily (it pre-calculates data for speed)

**Q: Not seeing recent activities**
- A: Activities are logged automatically as users use the system. Check back after users perform actions

**Q: Can't access analytics pages**
- A: Make sure you're logged in as Admin user. Analytics are only visible to admins

**Q: Want to see more details about an activity**
- A: Go to Audit Log, find the activity, and expand it to see full details including IP address and user agent

---

## 📈 Best Practices

✅ **Daily Reviews**: Check advanced analytics daily for early warning signs
✅ **Weekly Audits**: Review audit logs weekly for security
✅ **Monthly Reports**: Use branch snapshots for monthly performance reviews
✅ **Identify Trends**: Look at charts to spot patterns (good or bad)
✅ **Staff Feedback**: Use performance metrics to give constructive feedback
✅ **Optimize Workload**: Adjust staff assignments based on performance data
✅ **Compliance**: Keep audit logs for compliance and regulatory requirements

---

## 🎨 Customization

### Want to change what's tracked?
Edit `analytics/models.py` → `DetailedActivityLog.Action` class

### Want to add more charts?
Edit `templates/analytics/advanced_dashboard.html` and add Chart.js code

### Want to change analytics logic?
Edit `analytics/views.py` → `advanced_analytics` function

### Want to add new filtering?
Edit `templates/analytics/audit_log.html` filter form

---

## 📞 Need Help?

1. **Check Documentation**: Read `ANALYTICS_README.md` for detailed info
2. **Check Implementation**: Read `ANALYTICS_IMPLEMENTATION_SUMMARY.md` for architecture
3. **Check Admin Interface**: Go to `/admin/analytics/` to browse data directly
4. **Check Django Admin**: View logs and metrics in Django admin

---

## 🎯 Immediate Next Steps

1. **Right Now**: 
   - Navigate to `/analytics/advanced/` to see the dashboard
   - Explore the filters and time periods
   
2. **Today**:
   - Check the audit log to understand what's being tracked
   - View staff performance to see your team's activity
   
3. **This Week**:
   - Set up daily analytics generation (if not done)
   - Review the charts and understand your metrics
   - Share findings with your team
   
4. **This Month**:
   - Use branch performance data for reviews
   - Optimize staff workload based on analytics
   - Establish monthly analytics review meetings

---

## 🎉 You're All Set!

Your analytics system is **fully functional and ready to provide insights into your consultancy operations.** 

Start exploring and let the data guide your decisions! 📊

---

**For more information**, see:
- `ANALYTICS_README.md` - Full documentation
- `ANALYTICS_IMPLEMENTATION_SUMMARY.md` - Technical details
- `/admin/analytics/` - Django admin interface
