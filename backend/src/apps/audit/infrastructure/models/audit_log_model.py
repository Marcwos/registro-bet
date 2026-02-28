import uuid

from django.db import models


class AuditLogModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    action = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="idx_audit_created_at"),
            models.Index(fields=["action"], name="idx_audit_action"),
            models.Index(fields=["user_id"], name="idx_audit_user_id"),
        ]

    def __str__(self):
        return f"{self.action} - {self.user_id} - {self.created_at}"
