import pytest


@pytest.mark.django_db
class TestCityView:
    def test_getting_cities(self, client):
        response = client.get("/v2/cities/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 3

        assert {
            "latitude": "-6.79240000000",
            "longitude": "39.20830000000",
            "slug": "dar-es-salaam",
            "name": "Dar es Salaam",
            "country": "Tanzania",
            "label": "Dar es Salaam, Tanzania",
        } in data["results"]
