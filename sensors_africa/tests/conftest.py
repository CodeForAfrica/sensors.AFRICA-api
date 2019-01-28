
import pytest

from django.core.management import call_command

from feinstaub.sensors.models import (
    Sensor,
    SensorLocation,
    SensorType,
    Node,
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
    l, x = SensorLocation.objects.get_or_create(
        description='somewhere'
    )
    return l


@pytest.fixture
def sensor_type():
    st, x = SensorType.objects.get_or_create(
        uid="a",
        name="b",
        manufacturer="c"
    )
    return st


@pytest.fixture
def node(logged_in_user, location):
    n, x = Node.objects.get_or_create(
        uid='test123',
        owner=logged_in_user,
        location=location
    )
    return n


@pytest.fixture
def sensor(logged_in_user, sensor_type, node):
    s, x = Sensor.objects.get_or_create(
        node=node,
        sensor_type=sensor_type
    )
    return s
