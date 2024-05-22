import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SimulationEnviroment(models.Model):
    """Simulation Enviroment Object to be stored in the database"""

    simulation_environment_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    # volatility_model = models.ForeignKey(TypeVolitilityModel, models.DO_NOTHING)
    volatility = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    skew = models.FloatField(
        validators=[MinValueValidator(-0.1), MaxValueValidator(0.1)]
    )
    appreciation_percent = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)]
    )

    class Meta:
        db_table = "simulation_environment"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
