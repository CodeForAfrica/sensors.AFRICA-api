import pytest
import datetime
from django.utils import timezone


@pytest.mark.django_db
class TestGettingRawData:
    def test_getting_all_data(self, client, logged_in_user, sensors):
        response = client.get("/v1/data/", format="json")
        assert response.status_code == 200

        results = response.json()

        assert results["count"] == 8

    def test_getting_filtered_data_by_public_sensor(self, client, sensors):
        response = client.get("/v1/data/?sensor=%s" % sensors[0].id, format="json")
        assert response.status_code == 200

        results = response.json()

        # 8 Dar es Salaam SensorDatas
        # Only one senor is made public
        assert results["count"] == 8

    def test_getting_filtered_data_by_private_sensor(self, client, sensors):
        response = client.get("/v1/data/?sensor=%s" % sensors[1].id, format="json")
        assert response.status_code == 200

        results = response.json()

        assert results["count"] == 0

    def test_getting_filtered_data_by_timestamp(self, client):
        # Filter out one Dar es Salaam SensorData
        # It has timestamp 40 minutes ago
        timestamp = timezone.now() - datetime.timedelta(minutes=40)
        # It won't accept the tz information unless the '+' sign is encoded %2B
        timestamp = timestamp.replace(tzinfo=None)
        response = client.get("/v1/data/?timestamp__gte=%s" % timestamp, format="json")
        assert response.status_code == 200

        results = response.json()

        assert results["count"] == 7
