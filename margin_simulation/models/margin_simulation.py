import uuid

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from analysis.models import Analysis
from strategy_simulation.models import StrategySimulation
from api_gateway.models import TypeStatus


class MarginSimulation(models.Model):
    """Margin Simulation Object to be stored in the database"""

    SIMULATION_STATUS_CHOICES = (
        ("ENQUEUED", "ENQUEUED"),
        ("IN PROGRESS", "IN PROGRESS"),
        ("COMPLETED", "COMPLETED"),
        ("FAILED", "FAILED"),
    )

    name = models.CharField(max_length=100)
    margin_simulation_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    result_id = models.UUIDField(
        primary_key=False, auto_created=True, default=uuid.uuid4, editable=True
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    analysis = models.ForeignKey(
        "analysis.Analysis", models.DO_NOTHING, related_name="margin_simulation"
    )
    strategy_simulation = models.ForeignKey(
        "strategy_simulation.StrategySimulation", models.DO_NOTHING
    )
    type_status = models.ForeignKey("api_gateway.TypeStatus", models.DO_NOTHING)
    minimum_transfer_amount = models.DecimalField(
        max_digits=1000, decimal_places=2, validators=[MinValueValidator(0.0)]
    )
    initial_margin_percentage = models.FloatField(
        validators=[MinValueValidator(0.001), MaxValueValidator(1.0)]
    )
    variation_margin_percentage = models.FloatField(
        validators=[MinValueValidator(0.001), MaxValueValidator(1.0)]
    )
    pin = models.BooleanField(default=False)
    simulation_status = models.CharField(
        choices=SIMULATION_STATUS_CHOICES, default="ENQUEUED"
    )

    class Meta:
        db_table = "margin_simulation"
        ordering = ["-pin", "-date_updated"]

    @property
    def type(self):
        return "MARGIN"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        if kwargs.pop("new_result", True):
            self.result_id = uuid.uuid4()
        super().save(*args, **kwargs)
