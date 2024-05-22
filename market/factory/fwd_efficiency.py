from factory import Faker, LazyAttribute
from factory.django import DjangoModelFactory

from api_gateway.models import TypeCurrency
from market.models import FwdEfficiency


class FwdEfficiencyFactory(DjangoModelFactory):
    class Meta:
        model = FwdEfficiency

    name = Faker("word")
    base_currency = LazyAttribute(lambda _: TypeCurrency.objects.order_by("?").first())
    foreign_currency = LazyAttribute(
        lambda obj: TypeCurrency.objects.exclude(
            type_currency_id=obj.base_currency.type_currency_id
        )
        .order_by("?")
        .first()
    )
    duration = Faker("random_int", min=1, max=60)
