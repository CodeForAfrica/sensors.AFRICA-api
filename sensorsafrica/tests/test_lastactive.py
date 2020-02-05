import pytest
import pytz

from rest_framework.test import APIRequestFactory
from feinstaub.sensors.views import PostSensorDataView
from sensorsafrica.api.models import LastActiveNodes


@pytest.mark.django_db
class TestLastActiveSensor:
    def test_lastactive_command(self, sensors, last_active):
        sensors0_node = LastActiveNodes.objects.filter(
            node=sensors[0].node_id
        ).get()
        sensors3_node = LastActiveNodes.objects.filter(
            node=sensors[3].node_id
        ).get()
        sensors4_node = LastActiveNodes.objects.filter(
            node=sensors[4].node_id
        ).get()

        assert sensors0_node.last_data_received_at == last_active[0]
        assert sensors3_node.last_data_received_at == last_active[1]
        # Sensor is last active when they send the P1 and P2
        # Sensor[4] sent a none P1/P2 at timestamp last_active[2]
        assert sensors4_node.last_data_received_at != last_active[2]
