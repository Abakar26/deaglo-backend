from rest_framework import serializers


class SavedFromDeletedField(serializers.BooleanField):
    def to_representation(self, obj):
        # Convert model's is_deleted to is_saved for representation
        return not obj

    def to_internal_value(self, data):
        # Convert incoming is_saved to is_deleted for saving
        return not super().to_internal_value(data)
