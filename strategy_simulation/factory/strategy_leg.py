from factory.django import DjangoModelFactory
from factory import Faker

from strategy_simulation.models import StrategyLeg


class StrategyLegFactory(DjangoModelFactory):
    class Meta:
        model = StrategyLeg

    is_call = Faker("boolean")
    is_bought = Faker("boolean")
    premium = Faker("pydecimal", left_digits=6, right_digits=2, min_value=0.0)
    leverage = Faker("pyfloat", min_value=0.0, max_value=1.0)
    strike = Faker("pyfloat", min_value=-100, max_value=100)
    barrier_type = None
    barrier_level = None
