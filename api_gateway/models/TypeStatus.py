import uuid

from django.db import models


class TypeStatus(models.Model):
    """Type Status Object to be stored in the database"""

    type_status_id = models.UUIDField(
        primary_key=True, auto_created=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    class Meta:
        db_table = "type_status"
