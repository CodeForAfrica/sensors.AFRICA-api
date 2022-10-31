from rest_framework import serializers
from feinstaub.sensors.models import (
    Node,
    Sensor,
    SensorData,
    SensorDataValue,
    SensorLocation
)
from feinstaub.sensors.serializers import (
    NestedSensorLocationSerializer,
    NestedSensorDataSerializer,
    SensorDataSerializer as PostSensorDataSerializer
)

class NestedSensorSerializer(serializers.ModelSerializer):
    sensordatas = serializers.SerializerMethodField()

    class Meta:
        model = Sensor
        fields = ('id', 'description', 'pin', 'sensordatas')
    
    def get_sensordatas(self, obj):
        sensordatas = SensorData.objects.filter(sensor=obj).order_by('-timestamp')[:2]
        serializer = NestedSensorDataSerializer(instance=sensordatas, many=True)
        return serializer.data

class NodeLocationSerializer(NestedSensorLocationSerializer):
    class Meta(NestedSensorLocationSerializer.Meta):
        fields = NestedSensorLocationSerializer.Meta.fields + ("latitude", "longitude", "city")

class NodeSerializer(serializers.ModelSerializer):
    sensors = NestedSensorSerializer(many=True)
    location = NodeLocationSerializer()

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

class LastNotifySensorDataSerializer(PostSensorDataSerializer):

    def create(self, validated_data):
        sd = super().create(validated_data)
         # use node from authenticator
        successful_authenticator = self.context['request'].successful_authenticator
        node, pin = successful_authenticator.authenticate(self.context['request'])

        #sometimes we post historical data (eg: from other network)
        #this means we have to update last_notify only if current timestamp is greater than what's there
        if node.last_notify is None or node.last_notify < sd.timestamp: 
            node.last_notify = sd.timestamp
            node.save()

        return sd
