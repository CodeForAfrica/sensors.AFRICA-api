import pytest


@pytest.mark.django_db
class TestGettingRawData:
    def test_getting_all_data(self, client, sensors):
        response = client.get("/v1/data/", format="json")
        assert response.status_code == 200

    def test_getting_filtered_data_by_sensor(self, client, sensors):
        response = client.get("/v1/data/?sensor=%s" % sensors[0].id, format="json")
        assert response.status_code == 200

    def test_getting_filtered_data_by_timestamp(self, client):
        response = client.get("/v1/data/?timestamp__gte=2015-09-19%2023:20:15", format="json")
        assert response.status_code == 200
