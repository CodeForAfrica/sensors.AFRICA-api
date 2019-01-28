import pytest
import pytz

@pytest.mark.django_db
class TestGettingData:

    def test_getting_all_readings(self, client, datavalues):
        response = client.get('/v2/readings/', format='json')
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 4


    def test_getting_all_readings_by_city(self, client, datavalues):
        response = client.get('/v2/readings/?city=Dar es Salaam', format='json')
        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2


    def test_getting_all_readings(self, client, datavalues):
        response = client.get('/v2/readings/average', format='json')
        assert response.status_code == 200

        data = response.json()

        assert data['P2'] == 4