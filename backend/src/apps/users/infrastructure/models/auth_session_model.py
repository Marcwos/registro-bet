import uuid

from django.db import models


class AuthSessionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    refresh_token_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, default="")
    ip_address = models.GenericIPAddressField(default="0.0.0.0")

    class Meta:
        db_table = "auth_sessions"
