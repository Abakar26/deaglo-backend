from factory.django import DjangoModelFactory
from factory import Faker, Sequence, LazyAttribute
from organization.models import Organization
from random import random


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = Faker("word")
