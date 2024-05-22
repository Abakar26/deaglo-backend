from factory import Faker, LazyAttribute
from factory.django import DjangoModelFactory

from analysis.models import Analysis, TypeCategory
from api_gateway.models import TypeCurrency


class AnalysisFactory(DjangoModelFactory):
    class Meta:
        model = Analysis

    name = Faker("word")
    type_category = LazyAttribute(lambda _: TypeCategory.objects.order_by("?").first())
    base_currency = LazyAttribute(lambda _: TypeCurrency.objects.order_by("?").first())
    foreign_currency = LazyAttribute(
        lambda obj: TypeCurrency.objects.exclude(
            type_currency_id=obj.base_currency.type_currency_id
        )
        .order_by("?")
        .first()
    )
