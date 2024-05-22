from factory.django import DjangoModelFactory
from factory import Faker, Sequence, LazyAttribute, post_generation
from authentication.models import User, TypeUserRole
from random import random

from authentication.utils.user import user_init


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    @post_generation
    def initialize(self, create, extracted, **kwargs):
        user_init(self)

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttribute(
        lambda obj: "%s@example.com" % obj.first_name.lower() + str(random())
    )
    is_verified = True
    is_active = True
    city = Faker("city")
    country = Faker("country")
    type_user_role = LazyAttribute(lambda _: TypeUserRole.objects.order_by("?").first())
