import os
import uuid

from strategy_simulation.models import Strategy

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")


def populate_default_strategy(*args, **kwargs):
    values_to_insert = [
        (
            "007a4b59-a73f-422f-90bb-5ac05cac637d",
            False,
            "Call",
            "https://strategies-images.s3.us-east-2.amazonaws.com/Call.png",
            "A call offers upside if the spot rate rises. This can be used to hedge a short position in the underlying asset",
        ),
        (
            "a88cbfc8-12a5-41d0-8151-c869ed39b8b5",
            False,
            "Forward",
            "https://strategies-images.s3.us-east-2.amazonaws.com/Forward.png",
            "A forward is a contract which offers 100% protection downside, but zero upside potential. NB: This is not an option",
        ),
        (
            "482a966f-0f37-407b-9cb8-58b60c7e30e2",
            False,
            "Seagull",
            "https://strategies-images.s3.us-east-2.amazonaws.com/Seagull.png",
            "A Seagull consists of a long option, and two OTM positions: short call and short put. It offers downside protection and some upside. However, having two short legs results in higher tail risk in scenario where the rate moves too far from initial spot rate",
        ),
        (
            "2e754bea-a58a-4e96-87f7-adaea5356d20",
            False,
            "Put",
            "https://strategies-images.s3.us-east-2.amazonaws.com/Put.png",
            "A put offers upside if the spot rate falls. This can be used to offset losses in an underlying long position",
        ),
        (
            "37113527-54b2-4ce1-bf55-b077b810b395",
            False,
            "Participating forward",
            "https://strategies-images.s3.us-east-2.amazonaws.com/Par+fwd.png",
            "A participating forward consists of a long option covering 100% of the notional, and a short option covering 50% of the notional. The short leg offsets a portion of the long leg premium. It protects 100% against downside, but only offers 50% of the upside",
        ),
        (
            "5bd5fe24-079b-45a2-ab2b-17e717808bf7",
            False,
            "Collar",
            "https://strategies-images.s3.us-east-2.amazonaws.com/Collar.png",
            "A collar consists of a long OTM and a short OTM options. It limits the upside and the downside to a small range",
        ),
    ]

    # Insert values into the database
    for value in values_to_insert:
        try:
            Strategy.objects.update_or_create(
                strategy_id=uuid.UUID(value[0]),
                defaults=dict(
                    strategy_id=uuid.UUID(value[0]),
                    is_deleted=value[1],
                    sort_order=None,
                    name=value[2],
                    description=value[4],
                    image_url=value[3],
                ),
            )
        except Exception as e:
            print(value)
            print(e)
            raise Exception
