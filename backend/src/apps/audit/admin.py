from django.contrib import admin

from .infrastructure.models.audit_log_model import AuditLogModel


@admin.register(AuditLogModel)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user_id", "entity_type", "ip_address", "created_at")
    list_filter = ("action", "entity_type")
    search_fields = ("user_id", "action")
    ordering = ("-created_at",)
    readonly_fields = ("id", "user_id", "action", "entity_type", "entity_id", "metadata", "ip_address", "created_at")
