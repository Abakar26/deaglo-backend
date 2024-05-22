from factory.django import DjangoModelFactory
from factory import Faker

from strategy_simulation.models import StrategyInstance


class StrategyInstanceFactory(DjangoModelFactory):
    class Meta:
        model = StrategyInstance

    premium_override = Faker("pyfloat", min_value=0.0)
    leverage_override = Faker("pyfloat", min_value=0.0, max_value=1.0)
    strike_override = Faker("pyfloat", min_value=-100, max_value=100)
