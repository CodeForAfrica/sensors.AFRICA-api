from django.db import models
from django_extensions.db.models import TimeStampedModel
from feinstaub.sensors.models import Node, Sensor, SensorLocation


class SensorDataStat(TimeStampedModel):
    node = models.ForeignKey(Node)
    sensor = models.ForeignKey(Sensor)
    location = models.ForeignKey(SensorLocation)

    city_slug = models.CharField(max_length=255, db_index=True, null=False, blank=False)
    value_type = models.CharField(max_length=255, db_index=True, null=False, blank=False)

    average = models.FloatField(null=False, blank=False)
    maximum = models.FloatField(null=False, blank=False)
    minimum = models.FloatField(null=False, blank=False)

    # Number of data points averaged
    sample_size = models.IntegerField(default=0, null=False, blank=False)
    # Last datetime of calculated stats
    last_datetime = models.DateTimeField(null=True)

    date = models.DateField()

    def __str__(self):
        return "%s %s %s avg=%s min=%s max=%s" % (
            self.date,
            self.city_slug,
            self.value_type,
            self.average,
            self.minimum,
            self.maximum,
        )
