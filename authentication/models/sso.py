from django.db import models


class SSO(models.Model):
    user = models.OneToOneField(
        "authentication.User", on_delete=models.CASCADE, related_name="sso"
    )
    linkedin_id = models.CharField(max_length=255)
