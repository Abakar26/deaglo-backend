import uuid

from django.db import models


class FwdEfficiency(models.Model):
    """Fwd Efficiency Object to be stored in the database"""

    fwd_efficiency_id = models.UUIDField(
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
        related_name="fwdefficiency_base_currency_set",
    )
    foreign_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        db_column="foreign_currency_id",
        related_name="fwdefficiency_foreign_currency_set",
    )
    duration = models.IntegerField()

    class Meta:
        db_table = "fwd_efficiency"
        ordering = ("-date_updated", "-date_added")

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
