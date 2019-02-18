from rest_framework import serializers


class SensorDataStatSerializer(serializers.Serializer):
    average = serializers.FloatField()
    minimum = serializers.FloatField()
    maximum = serializers.FloatField()
    value_type = serializers.CharField(max_length=200)
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    city_slug = serializers.CharField(max_length=200)
