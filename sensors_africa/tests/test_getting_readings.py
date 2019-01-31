import pytest


@pytest.mark.django_db
class TestGettingData:
    def test_getting_all_readings(self, client, datavalues):
        response = client.get("/v2/air/readings/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data['count'] == 0

    def test_getting_all_readings_by_city(self, client, datavalues):
        response = client.get("/v2/air/readings/?city=Dar es Salaam", format="json")
        assert response.status_code == 200

        data = response.json()

        assert data['count'] == 3

    def test_getting_current_readings_by_city(self, client, datavalues):
        response = client.get("/v2/air/readings/now/?city=Dar es Salaam", format="json")
        assert response.status_code == 200

        data = response.json()

        print(data)

        assert len(data) == 2
        assert data[0]["city"] == "Dar es Salaam"
        assert data[0]["value_type"] == "P1"
        assert data[0]["average"] == 0.0
        assert data[0]["max"] == 0.0
        assert data[0]["min"] == 0.0

        assert data[1]["city"] == "Dar es Salaam"
        assert data[1]["value_type"] == "P2"
        assert data[1]["average"] == 4.5
        assert data[1]["max"] == 8.0
        assert data[1]["min"] == 1.0

    def test_getting_current_readings_all_cities(self, client, datavalues):
        response = client.get("/v2/air/readings/now/", format="json")
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2
        assert data[0]["city"] == "Dar es Salaam"
