import uuid

from django.db import models


class Organization(models.Model):
    """Organization Object to be stored in the database"""

    organization_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "organization"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
