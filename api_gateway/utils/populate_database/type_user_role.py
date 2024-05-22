import os
import uuid

from authentication.models import TypeUserRole

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")


def populate_user_role(*args, **kwargs):
    values_to_insert = [
        (
            "994110d2-e433-46c7-b172-add9b59c1343",
            False,
            "Provider",
            100,
            "A provider is someone who executes, hedges a strategy or analysis. They can only view the derivatives of the analysis.",
        ),
        (
            "b73d082d-f0f7-4d63-a44b-688f726dd26b",
            False,
            "Free Member",
            200,
            "A free member is someone that has very limited access to the application.",
        ),
        (
            "faa6e9b9-1048-473c-9f6e-aa906183c6da",
            False,
            "Premium Member",
            210,
            "A premium member is someone that has more access to the application than a free member.",
        ),
        (
            "c5b21bde-34e2-4e24-87c4-0c48f3114388",
            False,
            "Admin",
            300,
            "An admin is a member of an organization that manages other members of an organization.",
        ),
        (
            "c2c7c40c-56e1-4576-9309-7ca3fb7cac89",
            False,
            "Deaglo Admin",
            400,
            "A deaglo admin is a part of deaglo staff that adds organizations and creates account plans.",
        ),
    ]

    # Insert values into the database
    for value in values_to_insert:
        try:
            TypeUserRole.objects.update_or_create(
                type_user_role_id=uuid.UUID(value[0]),
                defaults=dict(
                    type_user_role_id=uuid.UUID(value[0]),
                    is_deleted=value[1],
                    name=value[2],
                    level=value[3],
                    description=value[4],
                ),
            )
        except Exception as e:
            print(e)
