from django.db.models import Model


class NonDeletedQuerySetMixin:
    def get_queryset(self):
        """
        Override the get_queryset method to exclude deleted records.
        """
        queryset = super().get_queryset()
        if issubclass(queryset.model, Model) and hasattr(queryset.model, "is_deleted"):
            return queryset.filter(is_deleted=False)
        return queryset
