import uuid

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class StrategyLegManager(models.Manager):
    def non_deleted(self):
        return self.get_queryset().filter(is_deleted=False)


class StrategyLeg(models.Model):
    """Custom Strategy Leg Object to be stored in the database"""

    strategy_leg_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    strategy = models.ForeignKey(
        "strategy_simulation.Strategy",
        models.DO_NOTHING,
        related_name="strategy_leg",
    )
    sort_order = models.IntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    is_call = models.BooleanField(blank=True, null=True)
    is_bought = models.BooleanField()
    premium = models.DecimalField(
        max_digits=1000, decimal_places=2, validators=[MinValueValidator(0.0)]
    )
    leverage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    strike = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(-100.0), MaxValueValidator(100.0)],
    )
    barrier_type = models.CharField(max_length=8, blank=True, null=True)
    barrier_level = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(-100.0), MaxValueValidator(100.0)],
    )
    objects = StrategyLegManager()

    class Meta:
        db_table = "strategy_leg"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
