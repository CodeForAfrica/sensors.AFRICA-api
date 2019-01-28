from rest_framework import mixins, viewsets, serializers

import django_filters

from django.db.models import Q, Subquery

from feinstaub.sensors.models import SensorData, SensorDataValue, SensorLocation

class SensorDataValueSerializer(serializers.ModelSerializer):

	class Meta:
		model = SensorDataValue
		fields = ('value', 'value_type',)

class SensorDataSerializer(serializers.ModelSerializer):
	sensordatavalues = SensorDataValueSerializer(many=True)

	class Meta:
		model = SensorData
		fields = ('sensordatavalues',)
		read_only = ('location')

class ReadingsView(mixins.ListModelMixin, 
									mixins.RetrieveModelMixin, 
									viewsets.GenericViewSet):
	queryset = SensorDataValue.objects.all()
	serializer_class = SensorDataValueSerializer
	
	def get_queryset(self):
		city = self.request.query_params.get('city')
		if city:
			sensor_data = SensorData.objects.filter(location=SensorLocation.objects.get(city=city))
			return SensorDataValue.objects.filter(sensordata__in=sensor_data)
		return SensorDataValue.objects.all()
