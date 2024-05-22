import os
import uuid

from api_gateway.models import TypeTool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")


def populate_tool(*args, **kwargs):
    values_to_insert = [
        (
            "3bb8e864-23a4-4871-890e-5476f09f6594",
            False,
            None,
            "Strategy Simulation",
            True,
            False,
            False,
        ),
        (
            "f6cf45a6-72ac-418a-ba11-1313aadafc7f",
            False,
            None,
            "Margin Simulation",
            True,
            False,
            False,
        ),
        (
            "67180b0e-5abe-4073-a346-9e70173da4d5",
            False,
            None,
            "Hedge IRR Simulation",
            True,
            False,
            False,
        ),
        (
            "410bed79-c6ce-40ac-8ff5-12dd9882022c",
            False,
            None,
            "Fwd Efficiency",
            False,
            True,
            False,
        ),
        (
            "0b21f439-d0ab-427a-9875-b201660b27f7",
            False,
            None,
            "Spot History",
            False,
            True,
            False,
        ),
        (
            "43c0bc4e-33b6-4aa3-8e2c-16088d6f885a",
            False,
            None,
            "Fx Movement",
            False,
            True,
            False,
        ),
        (
            "c4803434-b69d-404f-b56e-b0b384a67648",
            False,
            None,
            "Portfolio Stress Test",
            False,
            False,
            True,
        ),
        (
            "e65f0c20-3d4b-45d6-b9bf-427dcd8f02ea",
            False,
            None,
            "Portfolio Value At Risk",
            False,
            False,
            True,
        ),
        (
            "930619d8-c2ae-4113-ad97-29f5fb091f09",
            False,
            None,
            "Value At Risk",
            False,
            False,
            True,
        ),
        (
            "65fbb660-ae79-452d-8bd9-edfbf328a6f8",
            False,
            None,
            "Hedge Efficiency",
            False,
            False,
            True,
        ),
        (
            "a296952d-b907-4e21-b844-bc30731ae93e",
            False,
            None,
            "Expected Shortfall",
            False,
            False,
            True,
        ),
        (
            "d987042a-026b-4521-9a92-8ed5bf9d604f",
            False,
            None,
            "IM Collateral Drag",
            False,
            False,
            True,
        ),
        (
            "fa3d14d4-5e84-4cda-9c86-4c7c658f1404",
            False,
            None,
            "VM Collateral Drag",
            False,
            False,
            True,
        ),
    ]

    # Insert values into the database
    for value in values_to_insert:
        try:
            TypeTool.objects.update_or_create(
                type_tool_id=uuid.UUID(value[0]),
                defaults=dict(
                    type_tool_id=uuid.UUID(value[0]),
                    is_deleted=value[1],
                    sort_order=value[2],
                    name=value[3],
                    is_analysis_tool=value[4],
                    is_market_tool=value[5],
                    is_hedging_tool=value[6],
                ),
            )
        except Exception as e:
            print(e)
