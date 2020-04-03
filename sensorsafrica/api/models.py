from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils.text import slugify

from django.contrib.auth.models import User


class City(TimeStampedModel):
    city_slug = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    city_name = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    country_code = models.CharField(
        max_length=3, db_index=True, null=False, blank=False)

    class Meta:
        verbose_name_plural = "Cities"


class Location(TimeStampedModel):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    latitude = models.DecimalField(
        max_digits=14, decimal_places=11, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=14, decimal_places=11, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Locations"


class Node(TimeStampedModel):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    node_uid = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    node_owner = models.OneToOneField(User, on_delete=models.CASCADE)


class Sensor(TimeStampedModel):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    sensor_uid = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    sensor_name = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    sensor_manufacturer = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
