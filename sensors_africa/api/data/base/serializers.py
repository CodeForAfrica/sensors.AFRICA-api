from rest_framework import serializers


class ReadingsSerializer(serializers.Serializer):
    average = serializers.FloatField()
    day = serializers.DateTimeField()
    value_type = serializers.CharField(max_length=200)


class ReadingsNowSerializer(serializers.Serializer):
    average = serializers.FloatField()
    min = serializers.FloatField()
    max = serializers.FloatField()
    value_type = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=200)
