import uuid
from django.db import models
from market.models.FxCurrencyPair import FxCurrencyPair


class FxMovement(models.Model):
    """Fx Movement Object to be stored in the database"""

    fx_movement_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False, editable=False)

    user = models.ForeignKey("authentication.User", models.DO_NOTHING)

    name = models.CharField(max_length=100, blank=True, null=True)

    currency_pairs = models.ManyToManyField(
        FxCurrencyPair, db_column="fx_currency_pair_id"
    )

    duration = models.IntegerField()

    class Meta:
        db_table = "fx_movement"
        ordering = ("-date_updated", "-date_added")
