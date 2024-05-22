import uuid

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class StrategyInstance(models.Model):
    """Strategy Instance Map Object to be stored in the database"""

    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    strategy_simulation = models.ForeignKey(
        "strategy_simulation.StrategySimulation",
        models.DO_NOTHING,
        related_name="strategy_instance",
    )
    strategy_leg = models.ForeignKey(
        "strategy_simulation.StrategyLeg",
        models.DO_NOTHING,
        blank=True,
        null=True,
    )

    premium_override = models.DecimalField(
        max_digits=1000,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)],
    )
    leverage_override = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    strike_override = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(-100.0), MaxValueValidator(100.0)],
    )

    # this groups the legs to a certain strategy instance
    # for example, we have strategy A, and a strategy simulation can have multiple instances of A
    instance_group = models.IntegerField()

    class Meta:
        db_table = "strategy_instance"
