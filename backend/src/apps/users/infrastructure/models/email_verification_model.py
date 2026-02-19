import uuid

from django.db import models


class EmailVerificationModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    code_hash = models.CharField(max_length=255)
    purpose = models.CharField(max_length=50)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)

    class Meta:
        db_table = "email_verifications"
