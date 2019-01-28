from rest_framework import mixins, generics, viewsets, pagination

from feinstaub.sensors.serializers import SensorDataValueSerializer
from feinstaub.sensors.models import SensorData, SensorDataValue

class ReadingsView(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
	queryset = SensorDataValue.objects.all()
	serializer_class = SensorDataValueSerializer

	def get_queryset(self):
		return SensorDataValue.objects.all()