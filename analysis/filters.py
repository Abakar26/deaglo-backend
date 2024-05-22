from django_filters.rest_framework import FilterSet, CharFilter, BaseInFilter

from .models import Analysis


class CharInFilter(CharFilter, BaseInFilter):
    pass


class AnalysisFilter(FilterSet):
    base_currency = CharInFilter(field_name="base_currency__code", lookup_expr="in")
    foreign_currency = CharInFilter(
        field_name="foreign_currency__code", lookup_expr="in"
    )
    category = CharInFilter(field_name="type_category__name", lookup_expr="in")
    organization = CharFilter(field_name="organization__name", lookup_expr="iexact")

    class Meta:
        model = Analysis
        fields = ("base_currency", "foreign_currency", "type_category", "organization")

    def is_valid(self):
        keys = set(self.data.keys())
        keys.discard("page")
        keys.discard("with_simulations")
        keys.discard("order_by")

        instance_attributes = set(vars(self)["filters"].keys())
        if bool((keys - instance_attributes) & keys):
            return False
        return super().is_valid()
