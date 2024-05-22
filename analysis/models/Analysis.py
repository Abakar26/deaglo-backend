import uuid

from django.db import models

from authentication.models import User
from api_gateway.models import TypeCurrency
from analysis.models import TypeCategory
from django.core.exceptions import ValidationError


class Analysis(models.Model):
    """Analysis Object to be stored in the database"""

    analysis_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    # TODO! - research which FK we should change to CASCADE or SET NULL or keep DO NOTHING
    user = models.ForeignKey("authentication.User", models.DO_NOTHING)
    name = models.CharField(max_length=100)
    type_category = models.ForeignKey("analysis.TypeCategory", models.DO_NOTHING)
    base_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        related_name="analysis_base_currency_set",
    )
    foreign_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        related_name="analysis_foreign_currency_currency_set",
    )
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="analysis",
    )

    class Meta:
        db_table = "analysis"
        ordering = ("date_updated", "date_added")

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.strategy_simulation.update(is_deleted=True)
        for simulation in self.strategy_simulation.all():
            simulation.strategy_instance.update(is_deleted=True)
        self.margin_simulation.update(is_deleted=True)
        self.save()

    def clean(self, *args, **kwargs):
        if self.base_currency == self.foreign_currency:
            raise ValidationError(
                "base_currency and foreign_currency cannot be the same"
            )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save()
