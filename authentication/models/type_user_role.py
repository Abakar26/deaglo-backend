import uuid

from django.db import models


class TypeUserRole(models.Model):
    """
    Model for User Role
    """

    type_user_role_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=50)
    level = models.IntegerField()
    description = models.CharField(max_length=255)

    def delete(self, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "type_user_role"
