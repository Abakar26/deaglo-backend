from django.db.models import Q


class UserQuerySetMixin:
    def __init__(self, user_field=None, include_user_none=False):
        self.user_field = user_field or "user"
        self.include_user_none = include_user_none

    def get_queryset(self):
        """
        Override the get_queryset method to get items related to user in request context
        """
        user = self.request.user
        queryset = super().get_queryset()

        # If include_user_none is True, include objects where user_field is either the current user or None.
        if self.include_user_none:
            return queryset.filter(
                Q(**{self.user_field: user}) | Q(**{self.user_field + "__isnull": True})
            )
        else:
            return queryset.filter(**{self.user_field: user})
