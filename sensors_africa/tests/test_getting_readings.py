import pytest
import pytz

@pytest.mark.django_db
class TestGettingData:

    def test_getting_all_readings(self, client, datavalues):
        response = client.get('/v2/air/readings/', format='json')
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 11


    def test_getting_all_readings_by_city(self, client, datavalues):
        response = client.get('/v2/air/readings/?city=Dar es Salaam', format='json')
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 10


    def test_getting_current_readings_by_city(self, client, datavalues):
        response = client.get('/v2/air/readings/now/?city=Dar es Salaam', format='json')
        assert response.status_code == 200

        data = response.json()

        assert data["P2"]["average"] == 4.5
        assert data["P2"]["max"] == 8.0
        assert data["P2"]["min"] == 1.0

        assert data["P1"]["average"] == 0.0
        assert data["P1"]["max"] == 0.0
        assert data["P1"]["min"] == 0.0


    def test_getting_current_readings_all_cities(self, client, datavalues):
        response = client.get('/v2/air/readings/now/', format='json')
        assert response.status_code == 200

        data = response.json()

        assert not data["Dar es Salaam"] == None
        assert not data["Bagamoyo"] == None
        assert not data["Nairobi"] == None
        assert not data["Mombasa"] == None