from rest_framework import serializers


class SensorDataStatSerializer(serializers.Serializer):
    average = serializers.FloatField()
    minimum = serializers.FloatField()
    maximum = serializers.FloatField()
    date = serializers.DateField(required=False)
    value_type = serializers.CharField(max_length=200)
