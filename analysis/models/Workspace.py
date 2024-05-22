import uuid

from django.db import models


class Workspace(models.Model):
    """
    Represents a workspace Model
    """

    class Meta:
        db_table = "workspace"
        ordering = ("-date_updated", "-date_added")

    workspace_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    base_currency = models.ForeignKey(
        "api_gateway.TypeCurrency",
        models.DO_NOTHING,
        related_name="workspace_base_currency_set",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    user = models.ForeignKey("authentication.User", models.DO_NOTHING, "workspaces")
    analysis = models.ManyToManyField(
        "analysis.Analysis", related_name="workspace", blank=True
    )

    def delete(self, *args, **kwargs):
        """
        Deletes the workspace by setting the 'is_deleted' flag to True.
        """
        self.is_deleted = True
        self.save()
