from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('advanced/', views.advanced_analytics, name='advanced_dashboard'),
    path('audit-log/', views.activity_audit_log, name='audit_log'),
    path('user-performance/', views.user_performance_analytics, name='user_performance'),
    path('api/', views.analytics_api, name='api'),
]
