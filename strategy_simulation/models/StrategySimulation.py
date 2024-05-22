import uuid

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from rest_framework import status


class StrategySimulation(models.Model):
    """Strategy Simulation Object to be stored in the database"""

    SIMULATION_STATUS_CHOICES = (
        ("ENQUEUED", "ENQUEUED"),
        ("IN PROGRESS", "IN PROGRESS"),
        ("COMPLETED", "COMPLETED"),
        ("FAILED", "FAILED"),
    )

    name = models.CharField(max_length=100)
    strategy_simulation_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    result_id = models.UUIDField(
        primary_key=False, auto_created=True, default=uuid.uuid4, editable=True
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    analysis = models.ForeignKey(
        "analysis.Analysis", models.DO_NOTHING, related_name="strategy_simulation"
    )
    simulation_environment = models.ForeignKey(
        "analysis.SimulationEnviroment", models.DO_NOTHING
    )
    type_status = models.ForeignKey(
        "api_gateway.TypeStatus",
        models.DO_NOTHING,
        default="6f3d8caa-ca80-4117-8d03-c487c43338bc",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    notional = models.DecimalField(
        max_digits=1000, decimal_places=2, validators=[MinValueValidator(0.0)]
    )
    spot_rate_override = models.FloatField(blank=True, null=True)
    forward_rate_override = models.FloatField(blank=True, null=True)
    is_base_sold = models.BooleanField()
    initial_spot_rate = models.FloatField()
    initial_forward_rate = models.FloatField()
    spread = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    pin = models.BooleanField(default=False)
    simulation_status = models.CharField(
        choices=SIMULATION_STATUS_CHOICES, default="ENQUEUED"
    )

    class Meta:
        db_table = "strategy_simulation"
        ordering = ["-pin", "-date_updated"]

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.strategy_instance.update(is_deleted=True)
        self.save()

    def clean(self, *args, **kwargs):
        if self.end_date < self.start_date:
            raise ValidationError("start_date must preceed end_date")
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        if kwargs.pop("new_result", True):
            self.result_id = uuid.uuid4()
        super().save(*args, **kwargs)

    @property
    def type(self):
        return "STRATEGY"
