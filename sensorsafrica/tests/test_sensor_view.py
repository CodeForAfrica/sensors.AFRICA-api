import pytest
import datetime
from django.utils import timezone


@pytest.mark.django_db
class TestGettingSensorPast5MinutesData:
    def test_getting_past_5_minutes_data_for_sensor_with_id(self, client, sensors):
        response = client.get("/v1/sensors/%s/" % sensors[0].id, format="json")
        assert response.status_code == 200

        results = response.json()

        # 7 are recent since one the 8 data is 40 minutes ago
        assert len(results) == 7
        assert "sensordatavalues" in results[0]
        assert "timestamp" in results[0]
        assert "value_type" in results[0]['sensordatavalues'][0]
        assert "value" in results[0]['sensordatavalues'][0]
