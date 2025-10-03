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
from django.utils import timezone
from django.utils.text import slugify
from feinstaub.sensors.models import SensorData, SensorLocation
from sensorsafrica.api.models import LastActiveNodes


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        CKAN_ARCHIVE_API_KEY = os.environ.get("CKAN_ARCHIVE_API_KEY")
        CKAN_ARCHIVE_OWNER_ID = os.environ.get("CKAN_ARCHIVE_OWNER_ID")
        CKAN_ARCHIVE_URL = os.environ.get("CKAN_ARCHIVE_URL")

        session = requests.Session()
        session.verify = False

        ckan = ckanapi.RemoteCKAN(CKAN_ARCHIVE_URL, apikey=CKAN_ARCHIVE_API_KEY, session=session)

        # Get list of cities with active sensors in the last year
        # We are creating monthly archives for each city based on new data for the month
        # We only want to create packages for cities with active sensors in the last year
        # to avoid creating packages for cities that are no longer active. Historical data to last active date exists
        one_year_ago = timezone.now() - datetime.timedelta(days=365)
        city_queryset = (
            LastActiveNodes.objects.filter(last_data_received_at__gte=one_year_ago)
            .select_related("location")
            .values_list("location__city", flat=True)
            .order_by("location__city")
            .distinct()
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

            package_name = f"sensorsafrica-airquality-archive-{slugify(city)}"
            package_title = f"sensors.AFRICA Air Quality Archive {city}"

            try:
                package = ckan.action.package_show(id=package_name)
            except ckanapi.NotFound:
                try:
                    package = ckan.action.package_create(
                        owner_org=CKAN_ARCHIVE_OWNER_ID,
                        name=package_name,
                        title=package_title,
                        groups=[{"name": "sensorsafrica-airquality-archive"}]
                    )
                    self.stdout.write(self.style.SUCCESS("Created new package '%s' for city." % city))
                except ckanapi.ValidationError as e:
                    self.stderr.write(self.style.ERROR("Validation error creating package for city %s: %s" %city %e))
                    continue
            except Exception as e:
                self.stderr.write(self.style.ERROR("Unexpected error fetching package for city %s " %city %e))
                continue

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
                    .select_related("sensor","location")
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
                    fp = tempfile.NamedTemporaryFile(mode="w+b", suffix=".csv")
                    try:
                        self._write_file(fp, qs)
                        filepath = fp.name
                        self._create_or_update_resource(
                            resource_name, filepath, resources, ckan, package
                        )
                    finally:
                        # Cleanup temp file
                        fp.close()

                    # Don't DDOS openAFRICA
                    time.sleep(5)

                # Incriment month
                date = datetime.datetime(
                    day=1,
                    month=date.month % 12 + 1,
                    year=date.year + date.month // 12,
                    tzinfo=pytz.UTC,
                )

        self.stdout.write(self.style.SUCCESS("Data upload completed successfully."))

    @staticmethod
    def _write_file(fp, qs):
        fp.write(
            b"sensor_id;sensor_type;location;lat;lon;timestamp;value_type;value\n"
        )
        for sd in qs.iterator():
            lat = "{:.3f}".format(sd["location__latitude"]) if sd["location__latitude"] else "NULL"
            lon = "{:.3f}".format(sd["location__longitude"]) if sd["location__longitude"] else "NULL"

            s = ";".join([
                str(sd["sensor__id"]),
                sd["sensor__sensor_type__name"] or "NULL",
                str(sd["location__id"]),
                lat,
                lon,
                sd["timestamp"].isoformat(),
                sd["sensordatavalues__value_type"] or "NULL",
                str(sd["sensordatavalues__value"]),
            ])
            fp.write(bytes(s + "\n","utf-8"))

    def _create_or_update_resource(self, resource_name, filepath, resources, ckan, package):
        extension = "CSV"

        existing_resources = [
            r for r in resources
            if r.get("name") == resource_name and r.get("id")
        ]
        if existing_resources:
            resource_id = existing_resources[0]["id"]
            try:
                with open(filepath, "rb") as f:
                    ckan.action.resource_patch(
                        id=resource_id, upload=f
                    )
                self.stdout.write(self.style.SUCCESS("Updated resource: id=%s, name=%s" % (resource_id, resource_name)))
            except ckanapi.errors.ValidationError as e:
                self.stdout.write(self.style.ERROR("ValidationError during resource_update for id=%s, name=%s: %s" % (resource_id, resource_name, e)))
                return
        else:
            try:
                with open(filepath, "rb") as f:
                    ckan.action.resource_create(
                        package_id=package["id"],
                        name=resource_name,
                        format=extension,
                        url="upload",
                        upload=f,
                    )
                self.stdout.write(self.style.SUCCESS("Creating new resource: name=%s", resource_name))
            except ckanapi.errors.ValidationError as e:
                self.stderr.write(self.style.ERROR("ValidationError during resource_create for name=%s: %s") % (resource_name, e))
                return
