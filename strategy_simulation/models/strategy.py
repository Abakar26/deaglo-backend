import uuid

from django.db import models
from authentication.models import User


class StrategyManager(models.Manager):
    def custom_strategy(self, is_deleted=None, strategy_leg__is_deleted=None):
        query = self.get_queryset().exclude(created_by_user=None)
        if is_deleted is not None:
            query = query.filter(is_deleted=is_deleted)
        return query

    def default_strategy(self, is_deleted=None, strategy_leg__is_deleted=None):
        query = self.get_queryset().filter(created_by_user=None)
        if is_deleted is not None:
            query = query.filter(is_deleted=is_deleted)
        return query


class Strategy(models.Model):
    """
    Strategy Object to be stored in the database
    Includes both custom and default strategies
    """

    strategy_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    sort_order = models.IntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=250, blank=True, null=True)
    created_by_user = models.ForeignKey(
        "authentication.User",
        models.DO_NOTHING,
        blank=True,
        null=True,
    )
    objects = StrategyManager()

    class Meta:
        db_table = "strategy"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
