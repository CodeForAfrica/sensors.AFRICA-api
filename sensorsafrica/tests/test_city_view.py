import pytest


@pytest.mark.django_db
class TestCityView:
    def test_getting_cities(self, client, sensorsdatastats):
        response = client.get("/v2/cities/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 3
