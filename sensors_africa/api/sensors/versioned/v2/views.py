import datetime
from django.utils import timezone

from django.db.models import Q, Subquery

from rest_framework import mixins, generics, viewsets, pagination
from rest_framework.response import Response

from .models import Sensor, SensorData
from feinstaub.sensors.views import StandardResultsSetPagination

from .serializers import SensorSerializer


class SensorsView(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
	queryset = SensorData.objects.all()
	serializer_class = SensorSerializer
	pagination_class = StandardResultsSetPagination

	def get_queryset(self):
		active = self.request.query_params.get('active')
		if active:
			now = timezone.now()
			active_threshold = now - datetime.timedelta(minutes=30)

			if active == "1":
				data = SensorData.objects.filter(modified__gte=active_threshold)
				return Sensor.objects.filter(pk__in=Subquery(data.values('sensor')))
			
			if active == "0":
				last_notified = now - datetime.timedelta(minutes=30)
				data = SensorData.objects.filter(modified__lt=active_threshold)
				sensors_with_data = SensorData.objects.all().values('sensor')

				return Sensor.objects.filter(Q(pk__in=Subquery(data.values('sensor'))) | 
											~Q(pk__in=Subquery(sensors_with_data)))
			
		return Sensor.objects.all()
