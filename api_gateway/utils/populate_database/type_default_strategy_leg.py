import os
import uuid

from strategy_simulation.models import Strategy, StrategyLeg

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")


def populate_default_strategy_leg(*args, **kwargs):
    values_to_insert = [
        # Collar
        (
            "6beead00-4e23-44fa-8960-87cd4df1bb4c",
            False,
            "5bd5fe24-079b-45a2-ab2b-17e717808bf7",
            2,
            "https://strategies-images.s3.us-east-2.amazonaws.com/call_sold.png",
            True,
            False,
            1.0,
            0,
            -1.5,
            None,
            None,
        ),
        (
            "abbe8a47-d619-4f7f-b947-9ba35a4924ed",
            False,
            "5bd5fe24-079b-45a2-ab2b-17e717808bf7",
            1,
            "https://strategies-images.s3.us-east-2.amazonaws.com/put_bought.png",
            False,
            True,
            1.0,
            0,
            -2.0,
            None,
            None,
        ),
        # Seagull
        (
            "f8645b8e-569b-4461-ac9e-c13fac00ed11",
            False,
            "482a966f-0f37-407b-9cb8-58b60c7e30e2",
            1,
            "https://strategies-images.s3.us-east-2.amazonaws.com/put_bought.png",
            False,
            True,
            1.0,
            0,
            0.0,
            None,
            None,
        ),
        (
            "4ee6f2ed-87f0-489c-bb57-39f4c03ab128",
            False,
            "482a966f-0f37-407b-9cb8-58b60c7e30e2",
            2,
            "https://strategies-images.s3.us-east-2.amazonaws.com/call_sold.png",
            True,
            False,
            1.0,
            0,
            -7.0,
            None,
            None,
        ),
        (
            "fe45c81d-d8fe-4f9a-911a-27f37211db88",
            False,
            "482a966f-0f37-407b-9cb8-58b60c7e30e2",
            3,
            "https://strategies-images.s3.us-east-2.amazonaws.com/put_sold.png",
            False,
            False,
            1.0,
            0,
            -5.0,
            None,
            None,
        ),
        # Participating forward
        (
            "98ecc461-687c-40e4-8ae1-a74edead95f3",
            False,
            "37113527-54b2-4ce1-bf55-b077b810b395",
            1,
            "https://strategies-images.s3.us-east-2.amazonaws.com/put_bought.png",
            False,
            True,
            1.0,
            0,
            -3.0,
            None,
            None,
        ),
        (
            "2fdac258-f848-4947-bf5d-0179c1c62ead",
            False,
            "37113527-54b2-4ce1-bf55-b077b810b395",
            2,
            "https://strategies-images.s3.us-east-2.amazonaws.com/call_sold.png",
            True,
            False,
            0.5,
            0,
            3.0,
            None,
            None,
        ),
        # Call
        (
            "211df86b-74f6-4a89-9c01-4ddecc477925",
            False,
            "007a4b59-a73f-422f-90bb-5ac05cac637d",
            None,
            "https://strategies-images.s3.us-east-2.amazonaws.com/Call.png",
            True,
            True,
            1.0,
            0,
            -5.0,
            None,
            None,
        ),
        # Fwd
        (
            "5d2b3945-207f-48fe-a537-c29d5299d364",
            False,
            "a88cbfc8-12a5-41d0-8151-c869ed39b8b5",
            None,
            "https://strategies-images.s3.us-east-2.amazonaws.com/Forward.png",
            None,
            True,
            1.0,
            0,
            0.0,
            None,
            None,
        ),
        # Put
        (
            "b0de48dd-8287-4611-a3fb-9981b6ee479e",
            False,
            "2e754bea-a58a-4e96-87f7-adaea5356d20",
            None,
            "https://strategies-images.s3.us-east-2.amazonaws.com/Put.png",
            False,
            True,
            1.0,
            0,
            0.0,
            None,
            None,
        ),
    ]

    # Insert values into the database
    for value in values_to_insert:
        try:
            instance = Strategy.objects.get(pk=value[2])

            StrategyLeg.objects.update_or_create(
                strategy_leg_id=uuid.UUID(value[0]),
                defaults=dict(
                    strategy_leg_id=uuid.UUID(value[0]),
                    is_deleted=value[1],
                    strategy=instance,
                    sort_order=value[3],
                    image_url=value[4],
                    is_call=value[5],
                    is_bought=value[6],
                    leverage=value[7],
                    premium=value[8],
                    strike=value[9],
                    barrier_type=value[10],
                    barrier_level=value[11],
                ),
            )
        except Exception as e:
            print(e)
