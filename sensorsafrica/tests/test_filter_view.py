import pytest
import datetime
from django.utils import timezone


@pytest.mark.django_db
class TestGettingFilteringPast5MinutesData:
    def test_getting_past_5_minutes_data_for_sensor_type(self, client, sensor_type, sensordata):
        response = client.get("/v1/filter/?type=%s" % sensor_type.uid, format="json")
        assert response.status_code == 200

        results = response.json()

        # subtract 1 data since one the many data is set as posted 40 minutes ago, not 5 minutes
        assert len(results) == (len(list(filter(
            lambda sd: sd.sensor.sensor_type.uid == sensor_type.uid, sensordata))) - 1)

    def test_getting_past_5_minutes_data_for_sensor_city(self, client, sensordata):
        response = client.get("/v1/filter/?city=Bagamoyo", format="json")
        assert response.status_code == 200

        results = response.json()

        # no subtract 1 since the 1 data posted 40 minutes ago is for Dar es Salaam
        assert len(results) == (len(list(filter(
            lambda sd: sd.location.city == "Bagamoyo", sensordata))))

    def test_getting_past_5_minutes_data_for_sensor_country(self, client, sensordata):
        response = client.get("/v1/filter/?country=Tanzania", format="json")
        assert response.status_code == 200

        results = response.json()

        # subtract 1 data since one the many data in Tanzania is set as posted 40 minutes ago, not 5 minutes
        assert len(results) == (len(list(filter(
            lambda sd: sd.location.country == "Tanzania", sensordata))) - 1)
