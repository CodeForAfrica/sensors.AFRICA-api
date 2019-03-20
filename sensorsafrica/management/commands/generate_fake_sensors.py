from django.core.management import BaseCommand

from django.utils.text import slugify
from uuid import uuid4

import random

from django.contrib.auth import get_user_model
from feinstaub.sensors.models import Node, SensorLocation, SensorType, Sensor

from sensorsafrica import settings
import json

class Command(BaseCommand):
    help = (u'This command generates fake sensors.')

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        user_model = get_user_model()
        user = user_model.objects.get(username="admin")

        sensor_type, created = SensorType.objects.get_or_create(uid="fake", name="fake", manufacturer="fake")
        location, created = SensorLocation.objects.get_or_create(city="fake", description="fake")

        count = options['count']
        for i in range(0, count):
            node, created = Node.objects.get_or_create(uid='fake-%d' % i, owner=user, location=location)
            sensor, created = Sensor.objects.get_or_create(node=node, sensor_type=sensor_type, pin=1, public=True)
