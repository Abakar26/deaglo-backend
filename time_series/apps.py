from django.apps import AppConfig
from django.db.models.signals import post_migrate
from time_series.utils.spot_history_data import backfill_spot_history_data


class TimeSeriesConfig(AppConfig):
    name = "time_series"

    def ready(self):
        post_migrate.connect(backfill_spot_history_data, sender=self)
