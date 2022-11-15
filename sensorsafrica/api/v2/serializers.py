from rest_framework import serializers
from feinstaub.sensors.serializers import (
    NestedSensorLocationSerializer,
)
from feinstaub.sensors.models import Node, Sensor, SensorType, SensorLocation
from feinstaub.sensors.serializers import (VerboseSensorDataSerializer, )


class SensorDataStatSerializer(serializers.Serializer):
    calculated_average = serializers.FloatField()
    calculated_minimum = serializers.FloatField()
    calculated_maximum = serializers.FloatField()
    value_type = serializers.CharField(max_length=200)
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    city_slug = serializers.CharField(max_length=200)


class CitySerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=14, decimal_places=11)
    longitude = serializers.DecimalField(max_digits=14, decimal_places=11)
    slug = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=255)
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        return "{}, {}".format(obj.name, obj.country)


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ("id", "node", "description", "pin", "sensor_type", "public")


class SensorLocationSerializer(NestedSensorLocationSerializer):
    class Meta(NestedSensorLocationSerializer.Meta):
        fields = NestedSensorLocationSerializer.Meta.fields + (
            "longitude",
            "latitude",
            "altitude",
            "street_name",
            "street_number",
            "city",
            "country",
            "postalcode",
            "traffic_in_area",
            "oven_in_area",
            "industry_in_area",
            "owner",
        )


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = ("id", "uid", "name", "manufacturer")


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = (
            "id",
            "uid",
            "owner",
            "location",
            "name",
            "description",
            "height",
            "sensor_position",
            "email",
            "last_notify",
            "indoor",
            "inactive",
            "exact_location",
        )

class SensorDataSensorLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorLocation
        fields = ('id', "country", )

class SensorDataSerializer(VerboseSensorDataSerializer):
    location = SensorDataSensorLocationSerializer()
