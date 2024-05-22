from factory import Faker
from factory.django import DjangoModelFactory

from analysis.models import SimulationEnviroment


class SimulationEnvironmentFactory(DjangoModelFactory):
    class Meta:
        model = SimulationEnviroment

    name = Faker("word")
    volatility = Faker("pyfloat", min_value=0.0, max_value=1.0)
    skew = Faker("pyfloat", min_value=-0.1, max_value=0.1)
    appreciation_percent = Faker("pyfloat", min_value=-1.0, max_value=1.0)
