import uuid

from django.db import models


class BetModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    title = models.CharField(max_length=100)
    stake_amount = models.DecimalField(max_digits=12, decimal_places=2)
    odds = models.DecimalField(max_digits=8, decimal_places=2)
    profit_expected = models.DecimalField(max_digits=12, decimal_places=2)
    profit_final = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status_id = models.UUIDField()
    sport_id = models.UUIDField(null=True, blank=True)
    category_id = models.UUIDField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    is_freebet = models.BooleanField(default=False)
    is_boosted = models.BooleanField(default=False)
    placed_at = models.DateTimeField()
    settled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "bets"
        ordering = ["-placed_at"]

    def __str__(self):
        return self.title
