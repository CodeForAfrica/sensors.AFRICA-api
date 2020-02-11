from rest_framework import serializers


class RawSensorDataStatSerializer(serializers.Serializer):
    average = serializers.SerializerMethodField()
    minimum = serializers.SerializerMethodField()
    maximum = serializers.SerializerMethodField()
    value_type = serializers.SerializerMethodField()
    start_datetime = serializers.SerializerMethodField()
    end_datetime = serializers.SerializerMethodField()
    city_slug = serializers.SerializerMethodField()

    def get_city_slug(self, obj):
        return obj[0]

    def get_start_datetime(self, obj):
        return obj[1]

    def get_end_datetime(self, obj):
        return obj[2]

    def get_average(self, obj):
        return obj[3]

    def get_minimum(self, obj):
        return obj[4]

    def get_maximum(self, obj):
        return obj[5]

    def get_value_type(self, obj):
        return obj[6]


class CitySerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=14, decimal_places=11)
    longitude = serializers.DecimalField(max_digits=14, decimal_places=11)
    slug = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    country = serializers.CharField(max_length=255)
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        return "{}, {}".format(obj.name, obj.country)
