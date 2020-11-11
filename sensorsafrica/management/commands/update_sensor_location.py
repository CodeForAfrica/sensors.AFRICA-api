from datetime import datetime

from django.core.management import BaseCommand
from feinstaub.sensors.models import SensorLocation
from ...api.models import City


class Command(BaseCommand):
    help = "Update sensor locations with data from "

    def handle(self, *args, **options):
        cities = City.objects.all()

        for city in cities:
            SensorLocation.objects.get_or_create(
                location=city.name,
                city=city.slug,
                indoor=False
            )
