from rest_framework import serializers
from feinstaub.sensors.models import (
    Node,
    SensorData,
    SensorDataValue,
    SensorLocation
)
from feinstaub.sensors.serializers import (
    NestedSensorLocationSerializer,
    NestedSensorSerializer,
    SensorDataSerializer as PostSensorDataSerializer
)

class NodeSerializer(serializers.ModelSerializer):
    sensors = NestedSensorSerializer(many=True)
    location = NestedSensorLocationSerializer()

    class Meta:
        model = Node
        fields = ('id', 'sensors', 'uid', 'owner', 'location', 'last_notify')

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

class VerboseSensorDataSerializer(PostSensorDataSerializer):

    def create(self, validated_data):
        sd = super().create(validated_data)
         # use sensor from authenticator
        successful_authenticator = self.context['request'].successful_authenticator
        node, pin = successful_authenticator.authenticate(self.context['request'])
        node.last_notify = sd.timestamp
        node.save()

        return sd
