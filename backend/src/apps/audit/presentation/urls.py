from django.urls import path

from .views.admin_stats_view import AdminStatsView
from .views.audit_log_views import AuditLogListView

urlpatterns = [
    path("stats/", AdminStatsView.as_view(), name="admin_stats"),
    path("audit-logs/", AuditLogListView.as_view(), name="audit_log_list"),
]
