import uuid

from django.db import models


class SpotHistoryData(models.Model):
    date = models.DateField()
    currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=6)

    class Meta:
        db_table = "spot_history_data"
        unique_together = (("date", "currency"),)
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["date", "currency"]),
        ]
