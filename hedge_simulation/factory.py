from uuid import uuid4

import faker
from factory import Factory, LazyFunction
from factory import Faker, lazy_attribute

from analysis.factory import SimulationEnvironmentFactory
from hedge_simulation.models import HedgeSimulation


class HedgeSimulationFactory(Factory):
    """
    Factory for HedgeSimulation model.
    """

    class Meta:
        model = HedgeSimulation

    def __init__(self, analysis, file_url: str):
        self.analysis = analysis
        self.file_url = file_url

    hedge_irr_simulation_id = LazyFunction(uuid4)
    name = Faker("word")
    is_deleted = False
    fwd_rates = [
        [faker.generator.random.randint(1, 10_000) for _ in range(3)] for _ in range(3)
    ]
    start_date = "2024-01-29"
    end_date = "2024-01-29"

    @lazy_attribute
    def simulation_environment(self):
        return SimulationEnvironmentFactory()
