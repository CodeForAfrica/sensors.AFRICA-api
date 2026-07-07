import datetime

import pytest


@pytest.mark.postgres_only
@pytest.mark.django_db
class TestGettingDataFromLargeDataset:

    def test_getting_air_data_on_large_dataset(self, client, logged_in_user, large_sensorsdatastats):
        from django.utils import timezone
        from rest_framework.authtoken.models import Token
        token = Token.objects.get(user=logged_in_user)
        client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
        response = client.get(
            "/v2/data/stats/air/?city=dar-es-salaam&interval=month&from=%s" %
            large_sensorsdatastats["last_date"].date(),
            format="json",
        )
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 1

        assert type(data["results"][0]["P2"]) == list
        assert len(data["results"][0]["P2"]) == large_sensorsdatastats["months"]
