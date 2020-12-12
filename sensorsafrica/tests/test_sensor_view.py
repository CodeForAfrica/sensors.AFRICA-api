import pytest
import datetime
from django.utils import timezone

from rest_framework.test import APIRequestFactory

from feinstaub.sensors.models import Sensor
from sensorsafrica.api.v2.views import SensorsView


@pytest.mark.django_db
class TestSensorsView:
    @pytest.fixture
    def data_fixture(self):
        return {
            "pin": "1",
            "sensor_type": 1,
            "node": 1,
            "public": False,
        }

    def test_create_sensor(self, data_fixture, logged_in_user, node, sensor_type):
        data_fixture["node"] = node.id
        data_fixture["sensor_type"] = sensor_type.id
        factory = APIRequestFactory()
        url = "/v2/sensors/"
        request = factory.post(url, data_fixture, format="json")

        # authenticate request
        request.user = logged_in_user

        view = SensorsView
        view_function = view.as_view({"post": "create"})
        response = view_function(request)

        assert response.status_code == 201
        sensor = Sensor.objects.get(id=response.data["id"])
        assert sensor.pin == data_fixture["pin"]
        assert sensor.public == data_fixture["public"]

    def test_getting_past_5_minutes_data_for_sensor_with_id(self, client, sensors):
        response = client.get("/v1/sensors/%s/" % sensors[0].id, format="json")
        assert response.status_code == 200

        results = response.json()

        # 7 are recent since one the 8 data is 40 minutes ago
        assert len(results) == 7
        assert "sensordatavalues" in results[0]
        assert "timestamp" in results[0]
        assert "value_type" in results[0]["sensordatavalues"][0]
        assert "value" in results[0]["sensordatavalues"][0]
