import pytest


@pytest.mark.django_db
class TestGettingSensors:

    def test_get_active_sensors(self, client, datavalues):
        response = client.get('/v2/sensors/?active=1', format='json')
        assert response.status_code == 200

        data = response.json()
        
        assert data["count"] == 1


    def test_get_inactive_sensors(self, client, datavalues):
        response = client.get('/v2/sensors/?active=0', format='json')
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 3


    def test_get_inactive_and_active_sensors(self, client, datavalues):
        response = client.get('/v2/sensors/', format='json')
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 4


    def test_get_inactive_and_active_sensors(self, client, datavalues):
        response = client.get('/v2/sensors/?city=Dar es Salaam', format='json')
        assert response.status_code == 200

        data = response.json()

        assert data["count"] == 4