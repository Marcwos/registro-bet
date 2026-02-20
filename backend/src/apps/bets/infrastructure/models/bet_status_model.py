import uuid

from django.db import models


class BetStatusModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_final = models.BooleanField(default=False)

    class Meta:
        db_table = "bet_statuses"

    def __str__(self):
        return self.name
