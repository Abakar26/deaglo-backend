import uuid

from django.db import models


class TypeAnalysisRole(models.Model):
    """Type Analysis Role Object to be stored in the database"""

    type_analysis_role_id = models.UUIDField(primary_key=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    level = models.IntegerField()
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "type_analysis_role"
