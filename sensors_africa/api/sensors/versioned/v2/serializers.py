from rest_framework import serializers

from ...base.serializers import *
from ...base.models import SensorData

class SensorDataSensorSerializer(serializers.ModelSerializer):
    sensor = serializers.IntegerField(source='sensor.pk')

    class Meta:
        model = SensorData
        feilds = ('sensor',)
