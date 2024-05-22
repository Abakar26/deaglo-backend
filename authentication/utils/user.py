from market.models import FxCurrencyPair, FxMovement, SpotHistory, FwdEfficiency
from authentication.models import User

DEFAULT_FOREIGN_CURRENCY_LIST = [
    "1b35674b-caf9-4144-a40c-afee70a3cbb9",
    "1969f8bf-5b0c-4b7d-8a04-466ce27f6877",
    "c3cab86f-0cdb-4a15-8a06-5f714aed4026",
    "9dd97c25-c43f-466a-9bc4-fedc89ec9ff6",
    "360e8471-7b70-401f-ad05-b1b8fa521518",
    "e3f6218f-ee26-445c-a6d6-21c63a2d0ba5",
    "969b34b1-5e58-41af-96bd-c508a4b3536a",
]
DEFAULT_BASE_CURRENCY = "ebc1f86f-fca0-4341-8200-4e5c5af18683"
DEFAULT_FOREIGN_CURRENCY = "9dd97c25-c43f-466a-9bc4-fedc89ec9ff6"


def user_init(user: User):
    # Market tools initialization
    currency_pairs = []
    for foreign_currency in DEFAULT_FOREIGN_CURRENCY_LIST:
        instance, _ = FxCurrencyPair.objects.get_or_create(
            base_currency_id=DEFAULT_BASE_CURRENCY, foreign_currency_id=foreign_currency
        )
        currency_pairs.append(instance)

    fx_movement = FxMovement.objects.create(
        user=user, duration=12, is_default=True, name="FX Heatmap"
    )

    fx_movement.currency_pairs.set(currency_pairs)
    fx_movement.save()

    SpotHistory.objects.create(
        duration=24,
        base_currency_id=DEFAULT_BASE_CURRENCY,
        foreign_currency_id=DEFAULT_FOREIGN_CURRENCY,
        is_default=True,
        name="Spot History",
        user=user,
    )

    FwdEfficiency.objects.create(
        base_currency_id=DEFAULT_BASE_CURRENCY,
        foreign_currency_id=DEFAULT_FOREIGN_CURRENCY,
        is_default=True,
        user=user,
        duration=24,
        name="FWD Efficiency",
    )

    user.save()
