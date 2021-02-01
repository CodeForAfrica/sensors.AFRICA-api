from feinstaub.sensors.views import SensorFilter

class CustomSensorFilter(SensorFilter):
    class Meta(SensorFilter.Meta):
        # Pick the fields already defined and add the location__country field
        fields = {**SensorFilter.Meta.fields, **{'location__country': ['iexact']}}
