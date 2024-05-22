import os
import uuid

from analysis.models import TypeCategory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")


def populate_category(*args, **kwargs):
    values_to_insert = [
        ("3d9e421e-b088-4bab-9586-7409fe36407d", False, "Foreign share class"),
        ("4baf1976-0740-48fe-b3f5-93da2f71d662", False, "Operational fx"),
        ("409bd7ae-274b-45e5-b755-6534c2a89a62", False, "Foreign investment"),
    ]

    # Insert values into the database
    for value in values_to_insert:
        try:
            TypeCategory.objects.update_or_create(
                type_category_id=uuid.UUID(value[0]),
                defaults=dict(
                    type_category_id=uuid.UUID(value[0]),
                    is_deleted=value[1],
                    name=value[2],
                ),
            )
        except Exception as e:
            print(e)
