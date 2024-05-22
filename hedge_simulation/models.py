from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class HedgeSimulation(models.Model):
    class Meta:
        db_table = "hedge_simulation"
        ordering = ["-pin", "-date_updated"]

    SIMULATION_STATUS_CHOICES = (
        ("ENQUEUED", "ENQUEUED"),
        ("IN PROGRESS", "IN PROGRESS"),
        ("COMPLETED", "COMPLETED"),
        ("FAILED", "FAILED"),
    )

    hedge_irr_simulation_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False
    )
    result_id = models.UUIDField(
        primary_key=False, auto_created=True, default=uuid4, editable=True
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    analysis = models.ForeignKey(
        "analysis.Analysis", models.DO_NOTHING, related_name="hedge_simulation"
    )
    simulation_environment = models.ForeignKey(
        "analysis.SimulationEnviroment", models.DO_NOTHING
    )
    status = models.ForeignKey(
        "api_gateway.TypeStatus",
        models.DO_NOTHING,
        default="6f3d8caa-ca80-4117-8d03-c487c43338bc",
    )

    fwd_rates = ArrayField(
        ArrayField(
            models.FloatField(
                validators=[MinValueValidator(-10_000), MaxValueValidator(10_000)]
            ),
            size=3,
        ),
        size=3,
    )
    pin = models.BooleanField(default=False)
    simulation_status = models.CharField(
        choices=SIMULATION_STATUS_CHOICES, default="ENQUEUED"
    )

    @property
    def file_path(self):
        return f"{self.analysis.user_id}/{self.hedge_irr_simulation_id}-input.csv"

    def __str__(self):
        return str(self.hedge_irr_simulation_id)

    @property
    def type(self):
        return "HEDGE"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        if kwargs.pop("new_result", True):
            self.result_id = uuid4()
        super().save(*args, **kwargs)
