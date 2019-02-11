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
    return [
        SensorLocation.objects.get_or_create(city="Dar es Salaam", description="active")[0],
        SensorLocation.objects.get_or_create(city="Bagamoyo", description="inactive")[0],
        SensorLocation.objects.get_or_create(city="Mombasa", description="inactive")[0],
        SensorLocation.objects.get_or_create(city="Nairobi", description="inactive")[0],
        SensorLocation.objects.get_or_create(city="Dar es Salaam", description="active | some other node location")[0],
    ]


@pytest.fixture
def nodes(logged_in_user, locations):
    return [
        Node.objects.get_or_create(uid="0", owner=logged_in_user, location=locations[0])[0],
        Node.objects.get_or_create(uid="1", owner=logged_in_user, location=locations[1])[0],
        Node.objects.get_or_create(uid="2", owner=logged_in_user, location=locations[2])[0],
        Node.objects.get_or_create(uid="3", owner=logged_in_user, location=locations[3])[0],
        Node.objects.get_or_create(uid="4", owner=logged_in_user, location=locations[4])[0],
    ]


@pytest.fixture
def sensors(sensor_type, nodes):
    return [
        # Active Dar Sensor
        Sensor.objects.get_or_create(node=nodes[0], sensor_type=sensor_type)[0],
        # Inactive with last data push beyond active threshold
        Sensor.objects.get_or_create(node=nodes[1], sensor_type=sensor_type)[0],
        # Inactive without any data
        Sensor.objects.get_or_create(node=nodes[2], sensor_type=sensor_type)[0],
        # Active Nairobi Sensor
        Sensor.objects.get_or_create(node=nodes[3], sensor_type=sensor_type)[0],
        # Active Dar Sensor another location
        Sensor.objects.get_or_create(node=nodes[4], sensor_type=sensor_type)[0],
    ]


@pytest.fixture
def sensordata(sensors, locations):
    now = timezone.now()
    below_active_threshold_time = now - datetime.timedelta(minutes=40)

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
        sensor_datas.append(SensorData(sensor=sensors[3], location=locations[3]))

    # Dar es Salaam another node location SensorData
    for i in range(6):
        sensor_datas.append(SensorData(sensor=sensors[4], location=locations[4]))

    data = SensorData.objects.bulk_create(sensor_datas)

    # Bagamoyo Data is below active threshold
    data[0].update_modified = False
    data[0].modified = below_active_threshold_time
    data[0].save()

    return data


@pytest.fixture
def datavalues(sensors, sensordata):
    data_values = [
        # Bagamoyo
        SensorDataValue(sensordata=sensordata[0], value="2", value_type="humidity"),
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
            SensorDataValue(sensordata=sensordata[9 + i], value="0", value_type="P2")
        )

    # Dar es Salaam another node location SensorDataValues
    for i in range(6):
        data_values.append(SensorDataValue(sensordata=sensordata[109 + i], value="0.0", value_type="P2"))

    values = SensorDataValue.objects.bulk_create(data_values)

    # Set Dar es salaam a day ago's data
    values[1].update_modified = False
    values[1].created = timezone.now() - datetime.timedelta(days=1)
    values[1].save()
    values[2].update_modified = False
    values[2].created = timezone.now() - datetime.timedelta(days=1)
    values[2].save()


@pytest.fixture
def sensorsdatastats(datavalues):
    from django.core.management import call_command

    call_command("calculate_data_statistics")


@pytest.fixture
def additional_sensorsdatastats(sensors, locations, sensorsdatastats):
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

    from django.core.management import call_command

    call_command("calculate_data_statistics")
