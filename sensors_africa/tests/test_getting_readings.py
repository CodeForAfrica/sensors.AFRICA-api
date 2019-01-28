import pytest
import pytz

@pytest.mark.django_db
class TestGettingData:

    def test_getting_all_readings(self, client, datavalues):
        response = client.get('/v2/readings/', format='json')
        assert response.status_code == 200