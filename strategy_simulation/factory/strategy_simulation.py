from datetime import date, timedelta

from factory import Faker, lazy_attribute
from factory.django import DjangoModelFactory

from analysis.factory import SimulationEnvironmentFactory
from api_gateway.models import TypeStatus
from strategy_simulation.models import StrategySimulation


class StrategySimulationFactory(DjangoModelFactory):
    class Meta:
        model = StrategySimulation

    def __init__(self, analysis):
        self.analysis = analysis

    name = Faker("word")
    type_status = TypeStatus.objects.order_by("?").first()
    start_date = date.today()
    end_date = date.today() + timedelta(365)
    notional = Faker("pydecimal", min_value=1.0, right_digits=2)
    spot_rate_override = Faker("pyfloat", right_digits=2)
    forward_rate_override = Faker("pyfloat", right_digits=2)
    initial_spot_rate = Faker("pyfloat", right_digits=2)
    initial_forward_rate = Faker("pyfloat", right_digits=2)
    spread = Faker(
        "pyfloat", left_digits=0, right_digits=2, min_value=0.0, max_value=1.0
    )
    is_base_sold = Faker("boolean")

    @lazy_attribute
    def simulation_environment(self):
        simulaton_enviroment = SimulationEnvironmentFactory()
        return simulaton_enviroment
