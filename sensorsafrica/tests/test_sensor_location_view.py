import pytest
import datetime
from django.utils import timezone

from rest_framework.test import APIRequestFactory

from feinstaub.sensors.models import SensorLocation
from sensorsafrica.api.v2.views import SensorLocationsView


@pytest.mark.django_db
class TestSensorLocationsView:
    @pytest.fixture
    def data_fixture(self):
        return {
            "location": "Code for Africa Offices",
        }

    def test_create_sensor_location(self, data_fixture, logged_in_user):
        data_fixture["owner"] = logged_in_user.id
        factory = APIRequestFactory()
        url = "/v2/locations/"
        request = factory.post(url, data_fixture, format="json")

        # authenticate request
        request.user = logged_in_user

        view = SensorLocationsView
        view_function = view.as_view({"post": "create"})
        response = view_function(request)

        assert response.status_code == 201
        sensor_type = SensorLocation.objects.get(id=response.data["id"])

        assert sensor_type.location == data_fixture["location"]
        assert sensor_type.owner == logged_in_user
