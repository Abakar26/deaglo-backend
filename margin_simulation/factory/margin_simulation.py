from factory.django import DjangoModelFactory
from factory import Faker
from api_gateway.models import TypeStatus
from margin_simulation.models import MarginSimulation


class MarginSimulationFactory(DjangoModelFactory):
    class Meta:
        model = MarginSimulation

    def __init__(self, analysis):
        self.analysis = analysis

    name = Faker("word")
    type_status = TypeStatus.objects.order_by("?").first()
    minimum_transfer_amount = Faker("pyfloat", right_digits=2, min_value=0.001)
    initial_margin_percentage = Faker("pyfloat", min_value=0.001, max_value=1.0)
    variation_margin_percentage = Faker("pyfloat", min_value=0.001, max_value=1.0)
