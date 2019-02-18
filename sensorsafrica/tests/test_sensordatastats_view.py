import datetime

import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestGettingData:
    def test_getting_air_data_now(self, client, sensorsdatastats):
        response = client.get("/v2/air/data/dar-es-salaam/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 2

        results = data["results"]

        assert results[0]["value_type"] == "P1"
        assert results[0]["average"] == 0.0
        assert results[0]["maximum"] == 0.0
        assert results[0]["minimum"] == 0.0

        assert results[1]["value_type"] == "P2"

        # One node has an average of 5.5 for sample size 6
        # Another node has an average of 0 for sample size 6
        # The average for the city will be (5.5 * 6 + 0 * 6) / (6 + 6) = 2.75
        assert results[1]["average"] == 2.75

        assert results[1]["maximum"] == 8.0
        assert results[1]["minimum"] == 0.0

    def test_getting_air_data_now_all_cities(self, client, sensorsdatastats):
        response = client.get("/v2/air/data/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 4

        results = data["results"]

        assert results[0]["city_slug"] == "dar-es-salaam"
        assert results[0]["value_type"] == "P1"
        assert results[1]["city_slug"] == "dar-es-salaam"
        assert results[1]["value_type"] == "P2"
        assert results[2]["city_slug"] == "nairobi"
        assert results[3]["city_slug"] == "bagamoyo"

    def test_getting_air_data_value_type(self, client, sensorsdatastats):
        response = client.get(
            "/v2/air/data/dar-es-salaam/?value_type=P2", format="json"
        )
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 1
        assert data["results"][0]["value_type"] == "P2"

    def test_getting_air_data_from_date(self, client, sensorsdatastats):
        response = client.get(
            "/v2/air/data/dar-es-salaam/?from=%s"
            % (timezone.now() - datetime.timedelta(days=2)).date(),
            format="json",
        )
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 3

    def test_getting_air_data_from_date_to_date(self, client, sensorsdatastats):
        now = timezone.now()
        response = client.get(
            "/v2/air/data/dar-es-salaam/?from=%s&to=%s" % (now.date(), now.date()),
            format="json",
        )
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 2

    def test_getting_air_data_with_invalid_request(self, client, sensorsdatastats):
        response = client.get(
            "/v2/air/data/dar-es-salaam/?to=2019-02-08", format="json"
        )
        assert response.status_code == 400
        assert response.json() == {
            "from": "Must be provide along with to query"
        }

    def test_getting_air_data_with_invalid_from_request(self, client, sensorsdatastats):
        response = client.get(
            "/v2/air/data/dar-es-salaam/?from=2019-23-08", format="json"
        )
        assert response.status_code == 400
        assert response.json() == {
            "from": "Must be a date in the format Y-m-d."
        }

    def test_getting_air_data_with_invalid_to_request(self, client, sensorsdatastats):
        response = client.get(
            "/v2/air/data/dar-es-salaam/?from=2019-02-08&to=08-02-2019", format="json"
        )
        assert response.status_code == 400
        assert response.json() == {
            "to": "Must be a date in the format Y-m-d."
        }

    def test_getting_air_data_now_with_additional_values(
        self, client, additional_sensorsdatastats
    ):
        response = client.get("/v2/air/data/dar-es-salaam/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 2

        results = data["results"]

        assert results[0]["value_type"] == "P1"
        assert results[0]["average"] == 0.0
        assert results[0]["maximum"] == 0.0
        assert results[0]["minimum"] == 0.0

        assert results[1]["value_type"] == "P2"

        # The previous average was 2.75 for sample size 12
        # The addional data average is 4 for sample size 3
        # The new average is (2.75 * 12 + 4 * 3) / (12 + 3) = 3
        assert results[1]["average"] == 3

        assert results[1]["maximum"] == 8.0
        assert results[1]["minimum"] == 0.0
