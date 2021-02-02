import pytest
import datetime
from django.utils import timezone

from rest_framework.test import APIRequestFactory

from feinstaub.sensors.models import SensorType
from sensorsafrica.api.v2.views import SensorTypesView


@pytest.mark.django_db
class TestSensorTypesView:
    @pytest.fixture
    def data_fixture(self):
        return {
            "uid": "nm1",
            "name": "N1",
            "manufacturer": "M1",
        }

    def test_create_sensor_type(self, data_fixture, logged_in_user):
        factory = APIRequestFactory()
        url = "/v2/sensor-types/"
        request = factory.post(url, data_fixture, format="json")

        # authenticate request
        request.user = logged_in_user

        view = SensorTypesView
        view_function = view.as_view({"post": "create"})
        response = view_function(request)

        assert response.status_code == 201
        sensor_type = SensorType.objects.get(id=response.data["id"])

        assert sensor_type.name == data_fixture["name"]
        assert sensor_type.manufacturer == data_fixture["manufacturer"]
