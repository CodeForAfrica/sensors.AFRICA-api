import pytest
import datetime
from django.utils import timezone

from rest_framework.test import APIRequestFactory

from feinstaub.sensors.models import Node
from sensorsafrica.api.v2.views import NodesView


@pytest.mark.django_db
class TestNodesView:
    @pytest.fixture
    def data_fixture(self):
        return {
            "uid": "testnode1",
        }

    def test_create_node(self, data_fixture, logged_in_user, location):
        data_fixture["location"] = location.id
        data_fixture["owner"] = logged_in_user.id
        factory = APIRequestFactory()
        url = "/v2/nodes/"
        request = factory.post(url, data_fixture, format="json")

        # authenticate request
        request.user = logged_in_user

        view = NodesView
        view_function = view.as_view({"post": "create"})
        response = view_function(request)

        assert response.status_code == 201
        node = Node.objects.get(uid=response.data["uid"])
        assert node.uid == data_fixture["uid"]
        assert node.location == location
        assert node.owner == logged_in_user
