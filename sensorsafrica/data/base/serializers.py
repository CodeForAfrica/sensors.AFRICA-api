from rest_framework import serializers


class SensorDataStatSerializer(serializers.Serializer):
    average = serializers.FloatField()
    minimum = serializers.FloatField()
    maximum = serializers.FloatField()
    value_type = serializers.CharField(max_length=200)

    # date is optional:
    # It exists when _retrieve_range is invoked since its a daily average
    # It doesn't exist when _retrieve_past_24hrs is invoked since its possibly an average of two days
    date = serializers.DateField(required=False)
