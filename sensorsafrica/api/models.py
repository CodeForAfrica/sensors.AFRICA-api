from django.db import models
from django_extensions.db.models import TimeStampedModel
from feinstaub.sensors.models import Node, Sensor, SensorLocation
from django.utils.text import slugify


class City(TimeStampedModel):
    slug = models.CharField(max_length=255, db_index=True, null=False, blank=False)
    name = models.CharField(max_length=255, db_index=True, null=False, blank=False)
    country = models.CharField(max_length=255, db_index=True, null=False, blank=False)
    location = models.CharField(max_length=255, db_index=True, null=False, blank=False)
    latitude = models.DecimalField(max_digits=14, decimal_places=11, null=True, blank=True)
    longitude = models.DecimalField(max_digits=14, decimal_places=11, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Cities"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(City, self).save(*args, **kwargs)


class SensorDataStat(TimeStampedModel):
    node = models.ForeignKey(Node,on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor,on_delete=models.CASCADE)
    location = models.ForeignKey(SensorLocation,on_delete=models.CASCADE)

    city_slug = models.CharField(max_length=255, db_index=True, null=False, blank=False)
    value_type = models.CharField(max_length=255, db_index=True, null=False, blank=False)

    average = models.FloatField(null=False, blank=False)
    maximum = models.FloatField(null=False, blank=False)
    minimum = models.FloatField(null=False, blank=False)

    # Number of data points averaged
    sample_size = models.IntegerField(null=False, blank=False)
    # Last datetime of calculated stats
    last_datetime = models.DateTimeField()

    timestamp = models.DateTimeField()

    def __str__(self):
        return "%s %s %s avg=%s min=%s max=%s" % (
            self.timestamp,
            self.city_slug,
            self.value_type,
            self.average,
            self.minimum,
            self.maximum,
        )


class LastActiveNodes(TimeStampedModel):
    node = models.ForeignKey(Node,on_delete=models.CASCADE)
    location = models.ForeignKey(SensorLocation,on_delete=models.CASCADE)
    last_data_received_at = models.DateTimeField()

    class Meta:
        unique_together = ['node', 'location']
