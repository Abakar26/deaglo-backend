import uuid

from django.db import models

# from organization.models import Organization
# from authentication.models import User
from .Analysis import Analysis
from .TypeAnalysisRole import TypeAnalysisRole


class AnalysisOrganizationShareMap(models.Model):
    """Analysis Organization Share Map Object to be stored in the database"""

    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # organization = models.ForeignKey('deaglo_v2.Organization', models.DO_NOTHING)
    analysis = models.ForeignKey("analysis.Analysis", models.DO_NOTHING)
    # shared_by_user = models.ForeignKey('deaglo_v2.User', models.DO_NOTHING)
    type_analysis_role = models.ForeignKey(TypeAnalysisRole, models.DO_NOTHING)
    url = models.CharField(max_length=255)

    class Meta:
        db_table = "analysis_organization_share_map"
        unique_together = (("analysis", "organization"),)
