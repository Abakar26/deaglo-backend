import uuid

from django.db import models


class TypeCurrency(models.Model):
    """Type Currency Object to be stored in the database"""

    type_currency_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    sort_order = models.IntegerField(blank=True, null=True)
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    country_name = models.CharField(max_length=50)
    flag_url = models.CharField(max_length=300)
    is_analysis = models.BooleanField()
    is_spot_history = models.BooleanField()
    is_fwd_efficiency = models.BooleanField()
    is_fx_movement = models.BooleanField()

    class Meta:
        db_table = "type_currency"
        ordering = ["sort_order", "code"]
