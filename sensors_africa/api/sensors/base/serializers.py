from rest_framework import serializers

from feinstaub.sensors.models import SensorDataValue


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDataValue
        fields = ("value",)
