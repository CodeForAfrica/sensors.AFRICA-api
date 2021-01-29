from rest_framework import serializers
from feinstaub.sensors.models import (
    SensorData,
    SensorDataValue,
    SensorLocation
)
from feinstaub.sensors.serializers import (
    SensorDataValueSerializer
)

class SensorLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorLocation
        fields = '__all__'

class SensorDataSerializer(serializers.ModelSerializer):
    sensordatavalues = SensorDataValueSerializer(many=True)
    location = SensorLocationSerializer()

    class Meta:
        model = SensorData
        fields = ['location', 'timestamp', 'sensordatavalues']

class PostSensorDataSerializer(serializers.ModelSerializer):
    sensordatavalues = SensorDataValueSerializer(many=True)
    sensor = serializers.IntegerField(required=False,
                                      source='sensor.pk')

    class Meta:
        model = SensorData
        fields = ('sensor', 'sampling_rate', 'timestamp', 'sensordatavalues', 'software_version')
        read_only = ('location')

    def create(self, validated_data):
        # custom create, because of nested list of sensordatavalues

        sensordatavalues = validated_data.pop('sensordatavalues', [])
        if not sensordatavalues:
            raise exceptions.ValidationError('sensordatavalues was empty. Nothing to save.')

        # use sensor from authenticator
        successful_authenticator = self.context['request'].successful_authenticator
        if not successful_authenticator:
            raise exceptions.NotAuthenticated

        node, pin = successful_authenticator.authenticate(self.context['request'])
        if node.sensors.count() == 1:
            sensors_qs = node.sensors.all()
        else:
            sensors_qs = node.sensors.filter(pin=pin)
        sensor_id = sensors_qs.values_list('pk', flat=True).first()

        if not sensor_id:
            raise exceptions.ValidationError('sensor could not be selected.')
        validated_data['sensor_id'] = sensor_id

        # set location based on current location of sensor
        validated_data['location'] = node.location
        sd = SensorData.objects.create(**validated_data)

        SensorDataValue.objects.bulk_create(
            SensorDataValue(
                sensordata_id=sd.pk,
                **value,
            )
            for value in sensordatavalues
        )
        node.last_notify = sd.timestamp
        node.save()

        return sd
