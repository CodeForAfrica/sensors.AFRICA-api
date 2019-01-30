import pytest

import datetime
from django.utils import timezone
from django.core.management import call_command

from feinstaub.sensors.models import (
    Sensor,
    SensorLocation,
    SensorType,
    Node,
    SensorData,
    SensorDataValue,
)


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "auth.json")


@pytest.fixture
def logged_in_user():
    from django.contrib.auth import get_user_model

    user_model = get_user_model()

    user = user_model.objects.get(username="test")

    from rest_framework.authtoken.models import Token

    Token.objects.create(user=user)

    return user


@pytest.fixture
def location():
    l, x = SensorLocation.objects.get_or_create(description="somewhere")
    return l


@pytest.fixture
def sensor_type():
    st, x = SensorType.objects.get_or_create(uid="a", name="b", manufacturer="c")
    return st


@pytest.fixture
def node(logged_in_user, location):
    n, x = Node.objects.get_or_create(
        uid="test123", owner=logged_in_user, location=location
    )
    return n


@pytest.fixture
def sensor(logged_in_user, sensor_type, node):
    s, x = Sensor.objects.get_or_create(node=node, sensor_type=sensor_type)
    return s


@pytest.fixture
def locations():
    return SensorLocation.objects.bulk_create(
        [
            SensorLocation(city="Dar es Salaam", description="active"),
            SensorLocation(city="Bagamoyo", description="inactive"),
            SensorLocation(city="Mombasa", description="inactive"),
            SensorLocation(city="Nairobi", description="inactive"),
        ]
    )


@pytest.fixture
def nodes(logged_in_user, locations):
    return Node.objects.bulk_create(
        [
            Node(uid="0", owner=logged_in_user, location=locations[0]),
            Node(uid="1", owner=logged_in_user, location=locations[1]),
            Node(uid="2", owner=logged_in_user, location=locations[2]),
            Node(uid="3", owner=logged_in_user, location=locations[3]),
        ]
    )


@pytest.fixture
def sensors(sensor_type, nodes):
    return Sensor.objects.bulk_create(
        [
            Sensor(node=nodes[0], sensor_type=sensor_type),
            # Inactive with last data push beyond active threshold
            Sensor(node=nodes[1], sensor_type=sensor_type),
            # Inactive without any data
            Sensor(node=nodes[2], sensor_type=sensor_type),
            Sensor(node=nodes[3], sensor_type=sensor_type),
        ]
    )


@pytest.fixture
def sensordata(sensors, locations):
    now = timezone.now()
    below_active_threshold_time = now - datetime.timedelta(minutes=40)
    data = SensorData.objects.bulk_create(
        [
            # Bagamoyo SensorData
            SensorData(sensor=sensors[1], location=locations[1]),
            # Dar es Salaam SensorData
            SensorData(sensor=sensors[0], location=locations[0]),
            SensorData(sensor=sensors[0], location=locations[0]),
            SensorData(sensor=sensors[0], location=locations[0]),
            SensorData(sensor=sensors[0], location=locations[0]),
            SensorData(sensor=sensors[0], location=locations[0]),
            SensorData(sensor=sensors[0], location=locations[0]),
            SensorData(sensor=sensors[0], location=locations[0]),
            SensorData(sensor=sensors[0], location=locations[0]),
        ]
    )

    # Bagamoyo Data is below active threshold
    data[0].update_modified = False
    data[0].modified = below_active_threshold_time
    data[0].save()

    return data


@pytest.fixture
def datavalues(sensors, sensordata):
    return SensorDataValue.objects.bulk_create(
        [
            SensorDataValue(sensordata=sensordata[0], value="2", value_type="humidity"),
            SensorDataValue(sensordata=sensordata[1], value="1", value_type="P2"),
            SensorDataValue(sensordata=sensordata[2], value="2", value_type="P2"),
            SensorDataValue(sensordata=sensordata[3], value="3", value_type="P2"),
            SensorDataValue(sensordata=sensordata[4], value="4", value_type="P2"),
            SensorDataValue(sensordata=sensordata[5], value="5", value_type="P2"),
            SensorDataValue(sensordata=sensordata[6], value="6", value_type="P2"),
            SensorDataValue(sensordata=sensordata[7], value="7", value_type="P2"),
            SensorDataValue(sensordata=sensordata[8], value="0", value_type="P1"),
            SensorDataValue(sensordata=sensordata[8], value="8", value_type="P2"),
            SensorDataValue(
                sensordata=sensordata[8],
                value="some time stamp",
                value_type="timestamp",
            ),
        ]
    )
