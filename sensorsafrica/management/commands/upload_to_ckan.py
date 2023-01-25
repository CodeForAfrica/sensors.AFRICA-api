import calendar
import datetime
import os
import time
import datetime
import tempfile

import ckanapi
import requests
import pytz
from django.core.management import BaseCommand
from django.db.models import Max, Min
from django.utils.text import slugify
from feinstaub.sensors.models import SensorData, SensorLocation


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        CKAN_ARCHIVE_API_KEY = os.environ.get("CKAN_ARCHIVE_API_KEY")
        CKAN_ARCHIVE_OWNER_ID = os.environ.get("CKAN_ARCHIVE_OWNER_ID")
        CKAN_ARCHIVE_URL = os.environ.get("CKAN_ARCHIVE_URL")

        session = requests.Session()
        session.verify = False

        ckan = ckanapi.RemoteCKAN(CKAN_ARCHIVE_URL, apikey=CKAN_ARCHIVE_API_KEY, session=session)

        city_queryset = (
            SensorLocation.objects.all()
            .values_list("city", flat=True)
            .order_by("city")
            .distinct("city")
        )
        for city in city_queryset.iterator():
            # Ensure we have a city
            if not city or city.isspace():
                continue

            # Ensure city has actual data we can upload
            timestamp = SensorData.objects.filter(location__city=city).aggregate(
                Max("timestamp"), Min("timestamp")
            )
            if not timestamp or not timestamp['timestamp__min'] or not timestamp['timestamp__max']:
                continue

            try:
                package = ckan.action.package_create(
                    owner_org=CKAN_ARCHIVE_OWNER_ID,
                    name="sensorsafrica-airquality-archive-" + slugify(city),
                    title="sensors.AFRICA Air Quality Archive " + city,
                    groups=[{"name": "sensorsafrica-airquality-archive"}]
                )
            except ckanapi.ValidationError:
                package = ckan.action.package_show(
                    id="sensorsafrica-airquality-archive-" + slugify(city)
                )

            resources = package["resources"]

            start_date = None
            for resource in resources:
                date = resource["name"].replace("Sensor Data Archive", "")
                if date:
                    date = datetime.datetime.strptime(date, "%B %Y ")
                    if not start_date or date > start_date:
                        start_date = date

            if not start_date:
                start_date = timestamp["timestamp__min"].replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )

            end_date = timestamp["timestamp__max"].replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            start_date = start_date.replace(tzinfo=pytz.UTC)
            end_date = end_date.replace(tzinfo=pytz.UTC)

            date = start_date
            while date <= end_date:
                qs = (
                    SensorData.objects.filter(
                        sensor__public=True,
                        location__city=city,
                        timestamp__month=date.month,
                        timestamp__year=date.year,
                        sensordatavalues__value__isnull=False,
                    )
                    .values(
                        "sensor__id",
                        "sensor__sensor_type__name",
                        "location__id",
                        "location__latitude",
                        "location__longitude",
                        "timestamp",
                        "sensordatavalues__value_type",
                        "sensordatavalues__value",
                    )
                    .order_by("timestamp")
                )

                if qs.exists():
                    resource_name = "{month} {year} Sensor Data Archive".format(
                        month=calendar.month_name[date.month], year=date.year
                    )
                    temp = self._write_file(qs=qs)
                    filepath = temp.name
                   
                    self._create_or_update_resource(
                        resource_name, filepath, resources, ckan, package
                    )

                    # Cleanup temp file
                    temp.close()
                 
                    # Don't DDOS openAFRICA
                    time.sleep(5)

                # Incriment month
                date = datetime.datetime(
                    day=1,
                    month=date.month % 12 + 1,
                    year=date.year + date.month // 12,
                    tzinfo=pytz.UTC,
                )

    @staticmethod
    def _write_file(qs):
        fp = tempfile.NamedTemporaryFile(mode="w+b", suffix=".csv")
        fp.write(
            b"sensor_id;sensor_type;location;lat;lon;timestamp;value_type;value\n"
        )
        for sd in qs.iterator():
            s = ";".join(
                [
                    str(sd["sensor__id"]),
                    sd["sensor__sensor_type__name"],
                    str(sd["location__id"]),
                    "{:.3f}".format(sd["location__latitude"]),
                    "{:.3f}".format(sd["location__longitude"]),
                    sd["timestamp"].isoformat(),
                    sd["sensordatavalues__value_type"],
                    sd["sensordatavalues__value"],
                ]
            )
            fp.write(bytes(s + "\n","utf-8"))

        return fp

    @staticmethod
    def _create_or_update_resource(resource_name, filepath, resources, ckan, package):
        extension = "CSV"

        resource = list(
            filter(lambda resource: resource["name"] == resource_name, resources)
        )
        if resource:
            resource = ckan.action.resource_update(
                id=resource[0]["id"], url="upload", upload=open(filepath)
            )
        else:
            resource = ckan.action.resource_create(
                package_id=package["id"],
                name=resource_name,
                format=extension,
                url="upload",
                upload=open(filepath),
            )
