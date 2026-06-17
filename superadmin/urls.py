from django.urls import path

from . import views

app_name = 'superadmin'

urlpatterns = [
    # Authentication
    path('login/', views.superadmin_login, name='login'),
    path('logout/', views.superadmin_logout, name='logout'),

    # Dashboard & Management
    path('', views.superadmin_dashboard, name='dashboard'),
    path('database/', views.database_management, name='database_management'),
    path('statistics/', views.database_statistics, name='statistics'),

    # Backups & Exports/Imports
    path('backups/', views.backup_management, name='backups'),
    path('exports/', views.data_exports, name='exports'),
    path('imports/', views.data_imports, name='imports'),

    # Audit & Monitoring
    path('audit-log/', views.superadmin_audit_log, name='audit_log'),

    # AJAX Actions
    path('delete-record/', views.delete_record, name='delete_record'),
]
