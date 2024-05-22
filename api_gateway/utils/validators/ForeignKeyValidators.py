from typing import Any
from django.core.validators import MinLengthValidator, MaxLengthValidator


class ForeignKeyMinLengthValidator(MinLengthValidator):
    def __init__(self, model, column_name, min_value, **kwargs):
        self.model = model
        self.column_name = column_name
        super().__init__(min_value, **kwargs)

    def clean(self, x: Any) -> Any:
        return len(getattr(x, self.column_name))


class ForeignKeyMaxLengthValidator(MaxLengthValidator):
    def __init__(self, model, column_name, max_value, **kwargs):
        self.model = model
        self.column_name = column_name
        super().__init__(max_value, **kwargs)

    def clean(self, x: Any) -> Any:
        return len(getattr(x, self.column_name))
