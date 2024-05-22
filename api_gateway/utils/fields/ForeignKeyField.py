from rest_framework import serializers
from django.core.validators import MinLengthValidator, MaxLengthValidator
from api_gateway.utils.validators import (
    ForeignKeyMinLengthValidator,
    ForeignKeyMaxLengthValidator,
)


class ForeignKeyCharField(serializers.CharField):
    def __init__(self, model, column_name, **kwargs):
        self.model = model
        self.column_name = column_name
        super().__init__(**kwargs)

        # Remove min and max validators if appended in super().__init__
        # We really don't need this as the FK will validate if it's valid or not
        # But we keep some validation to help with swagger docs
        self.validators = [
            validator
            for validator in self.validators
            if not isinstance(validator, (MinLengthValidator, MaxLengthValidator))
        ]
        if self.min_length is not None:
            self.validators.append(
                ForeignKeyMinLengthValidator(model, column_name, self.min_length)
            )
        if self.max_length is not None:
            self.validators.append(
                ForeignKeyMaxLengthValidator(model, column_name, self.max_length)
            )

    def to_representation(self, value):
        return getattr(value, self.column_name, None)

    def to_internal_value(self, data):
        if (
            self.context.get("request", None)
            and self.context["request"].method == "PATCH"
            and data is None
        ):
            return None

        try:
            filter_kwargs = {f"{self.column_name}__iexact": data}
            return self.model.objects.get(**filter_kwargs)
        except self.model.DoesNotExist:
            message = f"Enter a valid value"
            raise serializers.ValidationError(message)


class ForeignKeyUUIDField(serializers.UUIDField):
    def __init__(self, model, column_name, **kwargs):
        self.model = model
        self.column_name = column_name
        super().__init__(**kwargs)

    def to_representation(self, value):
        return getattr(value, self.column_name, None)

    def to_internal_value(self, data):
        if (
            self.context.get("request", None)
            and self.context["request"].method == "PATCH"
            and data is None
        ):
            return None

        try:
            filter_kwargs = {f"{self.column_name}": data}
            return self.model.objects.get(**filter_kwargs)
        except self.model.DoesNotExist:
            message = f"Enter a valid value"
            raise serializers.ValidationError(message)
