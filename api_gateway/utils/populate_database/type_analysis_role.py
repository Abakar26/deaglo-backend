import os
import uuid

from analysis.models import TypeAnalysisRole

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")


def populate_analysis_role(*args, **kwargs):
    values_to_insert = [
        (
            "a4e1a9dc-9ad9-42ad-afac-782cf17b96df",
            False,
            "Viewer",
            200,
            "A viewer only has read abilities",
        ),
        (
            "4489e13b-a588-4895-ac73-096c295b1ea3",
            False,
            "Editor",
            300,
            "An editor has read and write abilities",
        ),
        (
            "9a29b804-74c8-47e2-be75-54dec1efee23",
            False,
            "Owner",
            400,
            "An owner has read and write abilities",
        ),
    ]

    # Insert values into the database
    for value in values_to_insert:
        try:
            TypeAnalysisRole.objects.update_or_create(
                type_analysis_role_id=uuid.UUID(value[0]),
                defaults=dict(
                    type_analysis_role_id=uuid.UUID(value[0]),
                    is_deleted=value[1],
                    name=value[2],
                    level=value[3],
                    description=value[4],
                ),
            )
        except Exception as e:
            print(e)
