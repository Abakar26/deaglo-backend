from factory.django import DjangoModelFactory
from factory import Faker, LazyAttribute
from market.models import SpotHistory
from api_gateway.models import TypeCurrency


class SpotHistoryFactory(DjangoModelFactory):
    class Meta:
        model = SpotHistory

    name = Faker("word")
    base_currency = LazyAttribute(lambda _: TypeCurrency.objects.order_by("?").first())
    foreign_currency = LazyAttribute(
        lambda _: TypeCurrency.objects.order_by("?").first()
    )
    duration = Faker("random_int", min=1, max=5)
