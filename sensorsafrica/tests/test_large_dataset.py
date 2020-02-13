import datetime

import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestGettingDataFromLargeDataset:

    def test_getting_air_data_on_large_dataset(self, client, large_sensorsdatastats):
        response = client.get(
            "/v2/data/air/?city=dar-es-salaam&interval=month&from=%s" %
            large_sensorsdatastats["last_date"].date(),
            format="json",
        )
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 1

        assert type(data["results"][0]["P2"]) == list
        assert len(data["results"][0]["P2"]) == large_sensorsdatastats["months"]
