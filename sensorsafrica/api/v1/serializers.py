from rest_framework import serializers
from feinstaub.sensors.models import (
    SensorData,
    SensorDataValue,
    SensorLocation
)


class SensorLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorLocation
        fields = '__all__'


class SensorDataValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorDataValue
        fields = ['value_type', 'value']


class SensorDataSerializer(serializers.ModelSerializer):
    sensordatavalues = SensorDataValueSerializer(many=True)
    location = SensorLocationSerializer()

    class Meta:
        model = SensorData
        fields = ['location', 'timestamp', 'sensordatavalues']
