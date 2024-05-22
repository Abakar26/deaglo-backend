import uuid

from django.db import models
from analysis.models import Analysis

# from authentication.models import User
from .TypeTool import TypeTool


class ServiceLogCore(models.Model):
    """Abstract Service Log Object"""

    # service_log_core_id = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)
    request_date = models.DateTimeField()
    request_json = models.JSONField()
    response_date = models.DateTimeField(blank=True, null=True)
    response_json = models.JSONField(blank=True, null=True)
    # analysis = models.ForeignKey("analysis.Analysis", models.DO_NOTHING, blank=True, null=True)
    # user = models.ForeignKey("authentication.User", models.DO_NOTHING, blank=True, null=True)
    # type_tool = models.ForeignKey("api_gateway.TypeTool", models.DO_NOTHING)
    has_error = models.BooleanField()
    error_description = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255)

    class Meta:
        abstract = True
