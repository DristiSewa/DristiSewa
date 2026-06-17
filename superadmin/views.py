import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import User
from applications.models import Application
from branches.models import Branch
from documents.models import Document
from followups.models import FollowUp
from students.models import Student

from .models import (
    SuperAdmin,
    DatabaseBackup,
    DataExport,
    DataImport,
    SuperAdminAuditLog,
    DatabaseStatistics,
)


def superadmin_login(request):
    """Superadmin login page."""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('superadmin:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if email and password:
            user = authenticate(request, username=email, password=password)
            if user and user.is_superuser:
                login(request, user)

                # Update login tracking
                try:
                    superadmin = SuperAdmin.objects.get(user=user)
                    superadmin.last_login = timezone.now()
                    superadmin.login_count += 1
                    superadmin.save(update_fields=['last_login', 'login_count'])

                    # Log audit
                    SuperAdminAuditLog.objects.create(
                        superadmin=superadmin,
                        action='LOGIN',
                        description=f'Superadmin logged in',
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    )
                except SuperAdmin.DoesNotExist:
                    pass

                return redirect('superadmin:dashboard')
            else:
                messages.error(request, 'Invalid superadmin credentials.')
        else:
            messages.error(request, 'Please enter both email and password.')

    return render(request, 'superadmin/login.html')


def superadmin_logout(request):
    """Superadmin logout."""
    if request.user.is_authenticated:
        try:
            superadmin = SuperAdmin.objects.get(user=request.user)
            SuperAdminAuditLog.objects.create(
                superadmin=superadmin,
                action='LOGOUT',
                description='Superadmin logged out',
                ip_address=get_client_ip(request),
            )
        except SuperAdmin.DoesNotExist:
            pass

    logout(request)
    return redirect('superadmin:login')


def require_superadmin(view_func):
    """Decorator to require superadmin access."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('superadmin:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@require_superadmin
def superadmin_dashboard(request):
    """Main superadmin dashboard with database overview."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return redirect('superadmin:login')

    # Get latest statistics
    stats = DatabaseStatistics.objects.first()

    # Calculate totals
    total_users = User.objects.count()
    total_students = Student.objects.count()
    total_applications = Application.objects.count()
    total_documents = Document.objects.count()
    total_branches = Branch.objects.count()

    # Get recent activity
    recent_audits = SuperAdminAuditLog.objects.filter(
        superadmin=superadmin
    ).select_related('superadmin')[:10]

    # Database health
    pending_actions = FollowUp.objects.filter(is_done=False).count()
    pending_documents = Document.objects.filter(status=Document.Status.PENDING).count()

    # Growth metrics
    today = timezone.localdate()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    new_students_week = Student.objects.filter(created_at__date__gte=week_ago).count()
    new_students_month = Student.objects.filter(created_at__date__gte=month_ago).count()
    new_apps_week = Application.objects.filter(created_at__date__gte=week_ago).count()
    new_apps_month = Application.objects.filter(created_at__date__gte=month_ago).count()

    # Visa success rate
    decided_apps = Application.objects.filter(
        status__in=[Application.Status.VISA_GRANTED, Application.Status.REJECTED]
    ).count()
    granted_apps = Application.objects.filter(
        status=Application.Status.VISA_GRANTED
    ).count()
    visa_success_rate = round((granted_apps / decided_apps * 100), 1) if decided_apps else 0

    # Recent backups
    recent_backups = DatabaseBackup.objects.filter(
        created_by=superadmin
    )[:5]

    # Recent exports
    recent_exports = DataExport.objects.filter(
        created_by=superadmin
    )[:5]

    context = {
        'superadmin': superadmin,
        'total_users': total_users,
        'total_students': total_students,
        'total_applications': total_applications,
        'total_documents': total_documents,
        'total_branches': total_branches,
        'pending_actions': pending_actions,
        'pending_documents': pending_documents,
        'new_students_week': new_students_week,
        'new_students_month': new_students_month,
        'new_apps_week': new_apps_week,
        'new_apps_month': new_apps_month,
        'visa_success_rate': visa_success_rate,
        'recent_audits': recent_audits,
        'recent_backups': recent_backups,
        'recent_exports': recent_exports,
        'stats': stats,
    }

    return render(request, 'superadmin/dashboard.html', context)


@login_required
@require_superadmin
def database_management(request):
    """Manage all database records."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return redirect('superadmin:login')

    # Get all tables and counts
    tables = {
        'Users': User.objects.count(),
        'Students': Student.objects.count(),
        'Branches': Branch.objects.count(),
        'Applications': Application.objects.count(),
        'Documents': Document.objects.count(),
        'Follow-ups': FollowUp.objects.count(),
    }

    # Selected table to browse
    selected_table = request.GET.get('table', 'Users')
    page = request.GET.get('page', 1)

    # Get table data
    if selected_table == 'Users':
        queryset = User.objects.all().order_by('-date_joined')
        columns = ['Email', 'Name', 'Role', 'Branch', 'Active', 'Joined']
    elif selected_table == 'Students':
        queryset = Student.objects.select_related('user').order_by('-created_at')
        columns = ['Name', 'Email', 'Branch', 'Country', 'Verified', 'Created']
    elif selected_table == 'Branches':
        queryset = Branch.objects.all().order_by('name')
        columns = ['Name', 'Location', 'Active', 'Created']
    elif selected_table == 'Applications':
        queryset = Application.objects.select_related('student').order_by('-created_at')
        columns = ['Student', 'Status', 'Country', 'Created', 'Updated']
    elif selected_table == 'Documents':
        queryset = Document.objects.select_related('student').order_by('-created_at')
        columns = ['Student', 'Type', 'Status', 'Created']
    elif selected_table == 'Follow-ups':
        queryset = FollowUp.objects.select_related('student').order_by('-created_at')
        columns = ['Student', 'Status', 'Scheduled', 'Created']
    else:
        queryset = User.objects.all().order_by('-date_joined')
        columns = ['Email', 'Name', 'Role', 'Branch', 'Active', 'Joined']

    # Pagination
    paginator = Paginator(queryset, 50)
    records = paginator.get_page(page)

    context = {
        'superadmin': superadmin,
        'tables': tables,
        'selected_table': selected_table,
        'columns': columns,
        'records': records,
        'total_pages': paginator.num_pages,
        'current_page': int(page),
    }

    return render(request, 'superadmin/database_management.html', context)


@login_required
@require_superadmin
def backup_management(request):
    """Manage database backups."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return redirect('superadmin:login')

    backups = DatabaseBackup.objects.filter(
        created_by=superadmin
    ).order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(backups, 20)
    backups_page = paginator.get_page(page)

    context = {
        'superadmin': superadmin,
        'backups': backups_page,
        'total_backups': backups.count(),
        'total_pages': paginator.num_pages,
        'current_page': int(page),
    }

    return render(request, 'superadmin/backup_management.html', context)


@login_required
@require_superadmin
def data_exports(request):
    """Manage data exports."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return redirect('superadmin:login')

    exports = DataExport.objects.filter(
        created_by=superadmin
    ).order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(exports, 20)
    exports_page = paginator.get_page(page)

    context = {
        'superadmin': superadmin,
        'exports': exports_page,
        'total_exports': exports.count(),
        'total_pages': paginator.num_pages,
        'current_page': int(page),
    }

    return render(request, 'superadmin/data_exports.html', context)


@login_required
@require_superadmin
def data_imports(request):
    """Manage data imports."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return redirect('superadmin:login')

    imports = DataImport.objects.filter(
        created_by=superadmin
    ).order_by('-created_at')

    page = request.GET.get('page', 1)
    paginator = Paginator(imports, 20)
    imports_page = paginator.get_page(page)

    context = {
        'superadmin': superadmin,
        'imports': imports_page,
        'total_imports': imports.count(),
        'total_pages': paginator.num_pages,
        'current_page': int(page),
    }

    return render(request, 'superadmin/data_imports.html', context)


@login_required
@require_superadmin
def superadmin_audit_log(request):
    """View complete superadmin audit log."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return redirect('superadmin:login')

    logs = SuperAdminAuditLog.objects.all().select_related('superadmin').order_by('-created_at')

    # Filters
    action = request.GET.get('action', '')
    admin = request.GET.get('admin', '')
    status = request.GET.get('status', '')

    if action:
        logs = logs.filter(action=action)
    if admin:
        logs = logs.filter(superadmin_id=admin)
    if status:
        logs = logs.filter(status=status)

    # Get unique values for filters
    action_choices = SuperAdminAuditLog._meta.get_field('action').choices
    admin_choices = SuperAdmin.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(logs, 50)
    logs_page = paginator.get_page(page)

    context = {
        'superadmin': superadmin,
        'logs': logs_page,
        'action_choices': action_choices,
        'admin_choices': admin_choices,
        'selected_action': action,
        'selected_admin': admin,
        'selected_status': status,
        'total_logs': logs.count(),
        'total_pages': paginator.num_pages,
        'current_page': int(page),
    }

    return render(request, 'superadmin/audit_log.html', context)


@login_required
@require_superadmin
def database_statistics(request):
    """View database statistics and health."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return redirect('superadmin:login')

    # Get all statistics
    all_stats = DatabaseStatistics.objects.all().order_by('-timestamp')[:30]

    # Current stats
    today = timezone.localdate()
    current_stats = {
        'total_users': User.objects.count(),
        'total_students': Student.objects.count(),
        'total_applications': Application.objects.count(),
        'total_documents': Document.objects.count(),
        'total_branches': Branch.objects.count(),
        'active_students': Student.objects.filter(user__is_active=True).count(),
        'archived_students': Student.objects.filter(is_archived=True).count(),
        'verified_students': Student.objects.filter(is_verified=True).count(),
    }

    # Growth metrics
    new_students_today = Student.objects.filter(created_at__date=today).count()
    new_applications_today = Application.objects.filter(created_at__date=today).count()

    context = {
        'superadmin': superadmin,
        'all_stats': all_stats,
        'current_stats': current_stats,
        'new_students_today': new_students_today,
        'new_applications_today': new_applications_today,
    }

    return render(request, 'superadmin/statistics.html', context)


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


@login_required
@require_superadmin
@require_http_methods(["POST"])
def delete_record(request):
    """Delete a record from the database."""
    try:
        superadmin = SuperAdmin.objects.get(user=request.user)
    except SuperAdmin.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Superadmin not found'})

    record_type = request.POST.get('type', '')
    record_id = request.POST.get('id', '')

    if not record_type or not record_id:
        return JsonResponse({'success': False, 'error': 'Invalid parameters'})

    try:
        if record_type == 'user':
            obj = User.objects.get(id=record_id)
        elif record_type == 'student':
            obj = Student.objects.get(id=record_id)
        elif record_type == 'application':
            obj = Application.objects.get(id=record_id)
        elif record_type == 'document':
            obj = Document.objects.get(id=record_id)
        elif record_type == 'branch':
            obj = Branch.objects.get(id=record_id)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid type'})

        # Log the action
        SuperAdminAuditLog.objects.create(
            superadmin=superadmin,
            action='BULK_DELETE',
            description=f'Deleted {record_type}: {obj}',
            affected_records=1,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        obj.delete()
        return JsonResponse({'success': True, 'message': f'{record_type.title()} deleted successfully'})

    except Exception as e:
        SuperAdminAuditLog.objects.create(
            superadmin=superadmin,
            action='BULK_DELETE',
            description=f'Failed to delete {record_type}: {str(e)}',
            status='FAILED',
            ip_address=get_client_ip(request),
        )
        return JsonResponse({'success': False, 'error': str(e)})
