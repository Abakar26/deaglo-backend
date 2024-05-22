from factory.django import DjangoModelFactory
from factory import Faker, LazyAttribute, post_generation
from random import randint
from market.models import FxCurrencyPair, FxMovement
from api_gateway.models import TypeCurrency


class FxMovementFactory(DjangoModelFactory):
    class Meta:
        model = FxMovement

    @post_generation
    def add_random_currency_pairs(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            num_currency_pairs = extracted
        else:
            num_currency_pairs = randint(1, 5)

        currency_pairs = []
        for _ in range(num_currency_pairs):
            base_currency = TypeCurrency.objects.order_by("?").first()
            foreign_currency = (
                TypeCurrency.objects.exclude(pk=base_currency.pk).order_by("?").first()
            )
            currency_pair, _ = FxCurrencyPair.objects.get_or_create(
                base_currency=base_currency, foreign_currency=foreign_currency
            )
            currency_pairs.append(currency_pair)
        self.currency_pairs.set(currency_pairs)

    name = Faker("word")
    duration = Faker("random_int", min=1, max=60)
