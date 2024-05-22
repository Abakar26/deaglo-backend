import os
import uuid

from api_gateway.models import TypeStatus

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")


def populate_status(*args, **kwargs):
    values_to_insert = [
        ("c566154a-84fa-4a2c-bb1b-cbda11ed6866", False, "Ready For Execution", "green"),
        ("89137355-7743-41f8-a7a2-51fbe6e556ae", False, "Confirmed", "green"),
        ("622c0735-0c5f-4a98-8c4b-39bacfb1f54a", False, "On Hold", "gray"),
        ("6f3d8caa-ca80-4117-8d03-c487c43338bc", False, "In Progress", "gray"),
        ("6a267320-6ef3-4987-a863-4e4474c0416c", False, "Need Review", "purple"),
    ]

    # Insert values into the database
    for value in values_to_insert:
        try:
            TypeStatus.objects.update_or_create(
                type_status_id=uuid.UUID(value[0]),
                defaults=dict(
                    type_status_id=uuid.UUID(value[0]),
                    is_deleted=value[1],
                    name=value[2],
                    color=value[3],
                ),
            )
        except Exception as e:
            print(e)
