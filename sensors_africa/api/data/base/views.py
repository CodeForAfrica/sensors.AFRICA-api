from rest_framework import mixins, viewsets, serializers

import django_filters

from django.db.models import Q, Subquery

from feinstaub.sensors.models import SensorData, SensorDataValue, SensorLocation

import datetime
from django.utils import timezone

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

from rest_framework.response import Response
from django.db.models import Avg, Max, Min, FloatField, Case, When, Q
from django.db.models.functions import Cast

class ReadingsNowView(viewsets.GenericViewSet):

	def get_location_stats(self, location):
		sensor_data = SensorData.objects.filter(location=location)

		lte = timezone.now()
		gte = lte - datetime.timedelta(24 * 60)

		stats = SensorDataValue.objects\
		.filter(sensordata__in=sensor_data, created__lte=lte, created__gte=gte, value_type='P2')\
		.annotate(float_value=Case(
			When(~Q(value_type='timestamp'), then=Cast('value', FloatField())),
			output_field=FloatField(),
			))\
			.aggregate(average=Avg('float_value'), max=Max('float_value'), min=Min('float_value'))
		
		return stats

	def list(self, request):
		city = request.query_params.get('city')
		if city:
			stats = self.get_location_stats(SensorLocation.objects.get(city=city))
		else:
			stats = {}
			for location in SensorLocation.objects.all():
				stats[location.city] = self.get_location_stats(location)

			return Response(stats)
		return Response({})