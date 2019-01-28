from rest_framework import serializers

from feinstaub.sensors.models import SensorData

class SensorDataSensorSerializer(serializers.ModelSerializer):
    sensor = serializers.IntegerField(source='sensor.pk')

    class Meta:
        model = SensorData
        feilds = ('sensor',)
