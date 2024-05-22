import uuid

from django.db import models


class SpotHistory(models.Model):
    """Spot History Object to be stored in the database"""

    spot_history_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey("authentication.User", models.DO_NOTHING)
    name = models.CharField(max_length=100, blank=True, null=True)

    base_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        db_column="base_currency_id",
        related_name="spothistory_base_currency_set",
    )
    foreign_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        db_column="foreign_currency_id",
        related_name="spothistory_foreign_currency_set",
    )

    duration = models.IntegerField()
    layered = models.BooleanField(default=True)

    class Meta:
        db_table = "spot_history"
        ordering = ("-date_updated", "-date_added")
