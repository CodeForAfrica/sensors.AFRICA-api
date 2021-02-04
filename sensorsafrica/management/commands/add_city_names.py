from django.core.management import BaseCommand
from django.db.models import Q

from geopy.geocoders import Nominatim

from feinstaub.sensors.models import Node


class Command(BaseCommand):
    help = "Adds city names to SensorLocation by geo reversing the SensorLocation longitude and latitude."

    def handle(self, *args, **options):
        geolocator = Nominatim(user_agent="sensors-api")
        all_nodes = Node.objects.filter(Q(location__city=None) |  Q(location__city=''))
        
        for node in all_nodes:
            try:
                location = geolocator.reverse(f"{node.location.latitude}, {node.location.longitude}")
            except Exception:
                # Nodes with location like Soul Buoy raises exceptions
                continue
            city = location.raw['address'].get('city')
            node.location.city = city
            node.save()
