import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


def _expiry_time():
    return timezone.now() + timezone.timedelta(minutes=5)


class OTP(models.Model):
    class Meta:
        db_table = "otp"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        "authentication.User", related_name="otp", on_delete=models.CASCADE
    )
    code = models.IntegerField()
    expired_at = models.DateTimeField(default=_expiry_time)

    @property
    def is_expired(self):
        return timezone.now() - self.expired_at >= timedelta(seconds=0)

    def __str__(self):
        return f"{self.code}"
