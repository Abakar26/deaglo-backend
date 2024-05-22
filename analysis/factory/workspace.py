from factory import Faker, LazyAttribute
from factory.django import DjangoModelFactory

from analysis.models import Workspace
from api_gateway.models import TypeCurrency


class WorkspaceFactory(DjangoModelFactory):
    """
    Factory for creating Workspace instances for testing purposes.
    """

    class Meta:
        model = Workspace

    name = Faker("word")  # Generates a random word for the name

    # Generates a base currency by selecting a random TypeCurrency object
    # from the database using Django's ORM
    base_currency = LazyAttribute(lambda _: TypeCurrency.objects.order_by("?").first())
