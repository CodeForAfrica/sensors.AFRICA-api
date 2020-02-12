from django.db import models
from django_extensions.db.models import TimeStampedModel
from feinstaub.sensors.models import Node, Sensor, SensorLocation
from django.utils.text import slugify


class City(TimeStampedModel):
    slug = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    name = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    country = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    location = models.CharField(
        max_length=255, db_index=True, null=False, blank=False)
    latitude = models.DecimalField(
        max_digits=14, decimal_places=11, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=14, decimal_places=11, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Cities"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(City, self).save(*args, **kwargs)


class LastActiveNodes(TimeStampedModel):
    node = models.ForeignKey(Node)
    location = models.ForeignKey(SensorLocation)
    last_data_received_at = models.DateTimeField()

    class Meta:
        unique_together = ['node', 'location']
