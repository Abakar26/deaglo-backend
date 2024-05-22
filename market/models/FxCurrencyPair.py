import uuid
from django.db import models


class FxCurrencyPair(models.Model):
    fx_currency_pair_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )

    base_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        db_column="base_currency_id",
        related_name="fxcurrency_base_currency_set",
    )
    foreign_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        db_column="foreign_currency_id",
        related_name="fxcurrency_foreign_currency_set",
    )

    class Meta:
        db_table = "fx_currency_pair"
