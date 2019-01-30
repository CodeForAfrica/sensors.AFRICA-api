import pytest
import pytz

@pytest.mark.django_db
class TestGettingData:

    def test_getting_all_readings(self, client, datavalues):
        response = client.get('/v2/readings/', format='json')
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 8


    def test_getting_all_readings_by_city(self, client, datavalues):
        response = client.get('/v2/readings/?city=Dar es Salaam', format='json')
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 8


    def test_getting_all_readings(self, client, datavalues):
        response = client.get('/v2/readings/now/?city=Dar es Salaam', format='json')
        assert response.status_code == 200

        data = response.json()

        assert data["average"] == 4.5
        assert data["max"] == 8.0
        assert data["average"] == 1.0


    def test_getting_all_readings(self, client, datavalues):
        response = client.get('/v2/readings/now/', format='json')
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 4