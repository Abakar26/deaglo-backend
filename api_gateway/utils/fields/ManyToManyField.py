from rest_framework import serializers


class ManyToManyCharField(serializers.ListField):
    # TODO! - pass in child min and max length as parameters not via kwargs
    def __init__(self, model, column_name, **kwargs):
        self.model = model
        self.column_name = column_name
        self.child_min_length = kwargs.pop("child_min_length", None)
        self.child_max_length = kwargs.pop("child_max_length", None)
        super().__init__(
            child=serializers.CharField(
                min_length=self.child_min_length,
                max_length=self.child_max_length,
                label=column_name,
            ),
            **kwargs,
        )

    def to_representation(self, value):
        return [getattr(item, self.column_name, None) for item in value.all()]

    def to_internal_value(self, data):
        if (
            self.context.get("request", None)
            and self.context["request"].method == "PATCH"
            and data is None
        ):
            return None

        try:
            internal_data = []
            for value in data:
                filter_kwargs = {f"{self.column_name}__iexact": value}
                internal_data.append(self.model.objects.get(**filter_kwargs))
            return internal_data
        except self.model.DoesNotExist:
            message = f"Enter a valid value"
            raise serializers.ValidationError(message)
