import datetime

import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestGettingData:
    def test_getting_air_readings_now(self, client, datavalues):
        response = client.get("/v2/air/readings/dar-es-salaam/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 2

        results = data["results"]

        assert results[0]["value_type"] == "P1"
        assert results[0]["average"] == 0.0
        assert results[0]["max"] == 0.0
        assert results[0]["min"] == 0.0

        assert results[1]["value_type"] == "P2"
        assert results[1]["average"] == 5.5
        assert results[1]["max"] == 8.0
        assert results[1]["min"] == 3.0

    def test_getting_air_readings_value_type(self, client, datavalues):
        response = client.get("/v2/air/readings/dar-es-salaam/?type=P2", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["value_type"] == "P2"

    def test_getting_air_readings_from_date(self, client, datavalues):
        response = client.get(
            "/v2/air/readings/dar-es-salaam/?from=%s"
            % (timezone.now() - datetime.timedelta(days=1)).date(),
            format="json",
        )
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 3

    def test_getting_air_readings_from_date_to_date(self, client, datavalues):
        now = timezone.now()
        response = client.get(
            "/v2/air/readings/dar-es-salaam/?from=%s&to=%s"
            % (str(now.date()), str(now.date())),
            format="json",
        )
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 2
