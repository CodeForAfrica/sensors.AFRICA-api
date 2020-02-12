import datetime

import pytest
from django.core.management import call_command
from django.utils import timezone
from feinstaub.sensors.models import (Node, Sensor, SensorData,
                                      SensorDataValue, SensorLocation,
                                      SensorType)


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
    st, x = SensorType.objects.get_or_create(
        uid="a", name="b", manufacturer="c")
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
    return [
        SensorLocation.objects.get_or_create(
            city="Dar es Salaam", country="Tanzania", description="active")[0],
        SensorLocation.objects.get_or_create(
            city="Bagamoyo", country="Tanzania", description="inactive")[0],
        SensorLocation.objects.get_or_create(
            city="Mombasa", country="Kenya", description="inactive")[0],
        SensorLocation.objects.get_or_create(
            city="Nairobi", country="Kenya", description="inactive")[0],
        SensorLocation.objects.get_or_create(
            city="Dar es Salaam", country="Tanzania", description="active | some other node location")[0],
    ]


@pytest.fixture
def nodes(logged_in_user, locations):
    return [
        Node.objects.get_or_create(
            uid="0", owner=logged_in_user, location=locations[0])[0],
        Node.objects.get_or_create(
            uid="1", owner=logged_in_user, location=locations[1])[0],
        Node.objects.get_or_create(
            uid="2", owner=logged_in_user, location=locations[2])[0],
        Node.objects.get_or_create(
            uid="3", owner=logged_in_user, location=locations[3])[0],
        Node.objects.get_or_create(
            uid="4", owner=logged_in_user, location=locations[4])[0],
    ]


@pytest.fixture
def sensors(sensor_type, nodes):
    return [
        # Active Dar Sensor
        Sensor.objects.get_or_create(
            node=nodes[0], sensor_type=sensor_type, public=True)[0],
        # Inactive with last data push beyond active threshold
        Sensor.objects.get_or_create(
            node=nodes[1], sensor_type=sensor_type)[0],
        # Inactive without any data
        Sensor.objects.get_or_create(
            node=nodes[2], sensor_type=sensor_type)[0],
        # Active Nairobi Sensor
        Sensor.objects.get_or_create(
            node=nodes[3], sensor_type=sensor_type)[0],
        # Active Dar Sensor another location
        Sensor.objects.get_or_create(
            node=nodes[4], sensor_type=sensor_type)[0],
    ]


@pytest.fixture(autouse=True)
def sensordata(sensors, locations):

    sensor_datas = [
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
    # Nairobi SensorData
    for i in range(100):
        sensor_datas.append(SensorData(
            sensor=sensors[3], location=locations[3]))

    # Dar es Salaam another node location SensorData
    for i in range(6):
        sensor_datas.append(SensorData(
            sensor=sensors[4], location=locations[4]))

    data = SensorData.objects.bulk_create(sensor_datas)

    data[1].update_modified = False
    data[1].timestamp = timezone.now() - datetime.timedelta(minutes=40)
    data[1].save()

    return data


@pytest.fixture(autouse=True)
def datavalues(sensors, sensordata):
    data_values = [
        # Bagamoyo
        SensorDataValue(
            sensordata=sensordata[0], value="2", value_type="humidity"),
        # Dar es salaam a day ago's data
        SensorDataValue(sensordata=sensordata[1], value="1", value_type="P2"),
        SensorDataValue(sensordata=sensordata[2], value="2", value_type="P2"),
        # Dar es salaam today's data avg 5.5
        SensorDataValue(sensordata=sensordata[3], value="3", value_type="P2"),
        SensorDataValue(sensordata=sensordata[4], value="4", value_type="P2"),
        SensorDataValue(sensordata=sensordata[5], value="5", value_type="P2"),
        SensorDataValue(sensordata=sensordata[6], value="6", value_type="P2"),
        SensorDataValue(sensordata=sensordata[7], value="7", value_type="P2"),
        SensorDataValue(sensordata=sensordata[8], value="0", value_type="P1"),
        SensorDataValue(sensordata=sensordata[8], value="8", value_type="P2"),
        SensorDataValue(
            sensordata=sensordata[8], value="some time stamp", value_type="timestamp"
        ),
    ]

    # Nairobi SensorDataValues
    for i in range(100):
        data_values.append(
            SensorDataValue(
                sensordata=sensordata[9 + i], value="0", value_type="P2")
        )

    # Dar es Salaam another node location SensorDataValues
    for i in range(6):
        data_values.append(SensorDataValue(
            sensordata=sensordata[109 + i], value="0.0", value_type="P2"))

    return SensorDataValue.objects.bulk_create(data_values)


@pytest.fixture
def modified_datavalues(datavalues):
    now = timezone.now()
    # Set Dar es salaam a day ago's data
    datavalues[1].sensordata.update_modified = False
    datavalues[1].sensordata.timestamp = now - datetime.timedelta(days=2)
    datavalues[1].sensordata.save()
    datavalues[2].sensordata.update_modified = False
    datavalues[2].sensordata.timestamp = now - datetime.timedelta(days=2)
    datavalues[2].sensordata.save()

    # Set data received at different hours
    datavalues[3].sensordata.update_modified = False
    datavalues[3].sensordata.timestamp = now - datetime.timedelta(hours=1)
    datavalues[3].sensordata.save()
    datavalues[4].sensordata.update_modified = False
    datavalues[4].sensordata.timestamp = now - datetime.timedelta(hours=2)
    datavalues[4].sensordata.save()
    datavalues[5].sensordata.update_modified = False
    datavalues[5].sensordata.timestamp = now - datetime.timedelta(hours=3)
    datavalues[5].sensordata.save()


@pytest.fixture
def additional_sensorsdatastats(sensors, locations, modified_datavalues):
    sensordata = SensorData.objects.bulk_create([
        SensorData(sensor=sensors[0], location=locations[0]),
        SensorData(sensor=sensors[0], location=locations[0]),
        SensorData(sensor=sensors[0], location=locations[0]),
    ])

    SensorDataValue.objects.bulk_create([
        # Dar es salaam today's additional datavalues avg 4 for P2
        SensorDataValue(sensordata=sensordata[0], value="4", value_type="P2"),
        SensorDataValue(sensordata=sensordata[1], value="4", value_type="P2"),
        SensorDataValue(sensordata=sensordata[2], value="4", value_type="P2"),
    ])


@pytest.fixture
def last_active(sensors, locations):
    timestamps = [
        timezone.now(),
        timezone.now() + datetime.timedelta(minutes=2),
        timezone.now() + datetime.timedelta(minutes=4)
    ]
    sensordata = SensorData.objects.bulk_create([
        SensorData(
            sensor=sensors[0], location=locations[0], timestamp=timestamps[0]),
        SensorData(
            sensor=sensors[3], location=locations[3], timestamp=timestamps[1]),
        SensorData(
            sensor=sensors[4], location=locations[4], timestamp=timestamps[2]),
    ])

    SensorDataValue.objects.bulk_create([
        SensorDataValue(
            sensordata=sensordata[0], value="4", value_type="P2"),
        SensorDataValue(
            sensordata=sensordata[1], value="4", value_type="P1"),
        # Won't be tracked as last active
        SensorDataValue(
            sensordata=sensordata[2], value="4", value_type="Temp"),
    ])

    from django.core.management import call_command

    call_command("cache_lastactive_nodes")

    return timestamps
