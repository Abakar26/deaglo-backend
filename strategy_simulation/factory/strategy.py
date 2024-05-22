from factory.django import DjangoModelFactory
from factory import Faker, post_generation
from random import randint

from strategy_simulation.models import Strategy
from .strategy_leg import StrategyLegFactory


class StrategyFactory(DjangoModelFactory):
    class Meta:
        model = Strategy

    @post_generation
    def create_legs(self, create, extracted, **kwargs):
        if not create:
            return
        num_legs = randint(1, 4)
        for _ in range(num_legs):
            StrategyLegFactory(strategy=self)

    name = Faker("word")
    description = Faker("word")
