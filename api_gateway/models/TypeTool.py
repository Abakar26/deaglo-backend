import uuid

from django.db import models


class TypeTool(models.Model):
    """Type Tool Object to be stored in the database"""

    type_tool_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    sort_order = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=50)
    is_analysis_tool = models.BooleanField()
    is_market_tool = models.BooleanField()
    is_hedging_tool = models.BooleanField()

    class Meta:
        db_table = "type_tool"
