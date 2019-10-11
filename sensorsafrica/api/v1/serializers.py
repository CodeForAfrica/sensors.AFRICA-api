from rest_framework import serializers
from feinstaub.sensors.models import (
    SensorData,
    SensorDataValue
)


class SensorDataValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDataValue
        fields = ['value_type', 'value']


class SensorDataSerializer(serializers.ModelSerializer):
    sensordatavalues = SensorDataValueSerializer(many=True)

    class Meta:
        model = SensorData
        fields = ['timestamp', 'sensordatavalues']
