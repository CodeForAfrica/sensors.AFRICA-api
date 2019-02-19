from rest_framework import serializers


class SensorDataStatSerializer(serializers.Serializer):
    average = serializers.FloatField()
    minimum = serializers.FloatField()
    maximum = serializers.FloatField()
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
    location = serializers.SerializerMethodField()

    def get_label(self, obj):
        return '{}, {}'.format(obj.name, obj.country)

    def get_location(self, obj):
        return '{}/{}/{}'.format(obj.map_zoom, obj.latitude, obj.longitude)
