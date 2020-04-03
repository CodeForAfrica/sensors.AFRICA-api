import pytest
from geohash import encode
from influxdb_pytest_plugin import TestResultDTO

import pytest_localstack

@pytest.fixture
def sensor_tags():
    return [
        {
            "node_uid": "0",
            "node_owner": "cfa",
            "sensor_uid": "a",
            "sensor_name": "b",
            "sensor_manufacturer": "c"
        }
    ]


@pytest.fixture
def location_tags():
    return {
        "dar-es-salaam": {
            "lat": -6.7924,
            "lng": 39.2083,
            "country": "TZ",
            "city": "dar-es-salaam",
            "geohash": encode(-6.7924, 39.2083)
        },
        "bagamoyo": {
            "lat": -6.4456,
            "lng": 38.8989,
            "country": "TZ",
            "city": "bagamoyo",
            "geohash": encode(-6.4456, 38.8989)
        },
        "mombasa": {
            "lat": -4.0435,
            "lng": 39.6682,
            "country": "KE",
            "city": "mombasa",
            "geohash": encode(-4.0435, 39.6682)
        },
        "nairobi": {
            "lat": -1.2921,
            "lng": 36.8219,
            "country": "KE",
            "city": "nairobi",
            "geohash": encode(-1.2921, 36.8219)
        },
        "sinza": {
            "lat": -6.7829,
            "lng": 39.2246,
            "country": "TZ",
            "city": "dar-es-salaam",
            "geohash": encode(-6.7829, 39.2246)
        }
    }


@pytest.fixture
def sensors(sensor_tags, location_tags):
    return {
        "dar-es-salaam": {**location_tags["dar-es-salaam"], **sensor_tags[0]},
        "bagamoyo": {**location_tags["bagamoyo"], **sensor_tags[0]},
        "mombasa": {**location_tags["mombasa"], **sensor_tags[0]},
        "nairobi": {**location_tags["nairobi"], **sensor_tags[0]},
        "sinza": {**location_tags["sinza"], **sensor_tags[0]}
    }


@pytest.fixture(scope='function', autouse=True)
def values(request, sensors):
    data_values = []

    for i in range(100):
        test_result_dto = TestResultDTO()
        test_name = request.node.nodeid

        TestResultDTO.set_tag_values(
            test_result_dto, test_name, sensors["nairobi"])
        TestResultDTO.set_field_values(test_result_dto, test_name,  {
            "P2": 2,
            "P1": 1
        })

    for i in range(100):
        test_result_dto = TestResultDTO()
        test_name = request.node.nodeid

        TestResultDTO.set_tag_values(
            test_result_dto, test_name, sensors["sinza"])
        TestResultDTO.set_field_values(test_result_dto, test_name,  {
            "P2": 2,
            "P1": 1
        })

    for i in range(100):
        test_result_dto = TestResultDTO()
        test_name = request.node.nodeid

        TestResultDTO.set_tag_values(
            test_result_dto, test_name, sensors["dar-es-salaam"])
        TestResultDTO.set_field_values(test_result_dto, test_name,  {
            "P2": 2,
            "P1": 1
        })


# @pytest.fixture
# def sensorsdatastats(datavalues):
#     from django.core.management import call_command

#     call_command("calculate_data_statistics")


# @pytest.fixture
# def additional_sensorsdatastats(sensors, locations, sensorsdatastats):
#     sensordata = SensorData.objects.bulk_create([
#         SensorData(sensor=sensors[0], location=locations[0]),
#         SensorData(sensor=sensors[0], location=locations[0]),
#         SensorData(sensor=sensors[0], location=locations[0]),
#     ])

#     SensorDataValue.objects.bulk_create([
#         # Dar es salaam today's additional datavalues avg 4 for P2
#         SensorDataValue(sensordata=sensordata[0], value="4", value_type="P2"),
#         SensorDataValue(sensordata=sensordata[1], value="4", value_type="P2"),
#         SensorDataValue(sensordata=sensordata[2], value="4", value_type="P2"),
#     ])

#     from django.core.management import call_command

#     call_command("calculate_data_statistics")


# @pytest.fixture
# def large_sensorsdatastats(sensors, locations):

#     now = timezone.now()
#     months = 6
#     points = math.floor(
#         (now - (now - relativedelta(months=months-1))).days * 24 * 60 / 5)
#     minutes = points * 5 * months
#     for point in range(1, points):
#         created_sd = SensorData.objects.create(
#             sensor=sensors[0], location=locations[0])
#         created_sv = SensorDataValue.objects.create(
#             sensordata=created_sd, value="4", value_type="P2")
#         created_sv.update_modified = False
#         created_sv.created = now - datetime.timedelta(minutes=point * 5)
#         created_sv.save()

#         last_date = created_sv.created

#     from django.core.management import call_command

#     call_command("calculate_data_statistics")

#     return {
#         'months': months,
#         'minutes': minutes,
#         'last_date': last_date
#     }


# @pytest.fixture
# def last_active(sensors, locations, sensorsdatastats):
#     timestamps = [
#         timezone.now(),
#         timezone.now() + datetime.timedelta(minutes=2),
#         timezone.now() + datetime.timedelta(minutes=4)
#     ]
#     sensordata = SensorData.objects.bulk_create([
#         SensorData(
#             sensor=sensors[0], location=locations[0], timestamp=timestamps[0]),
#         SensorData(
#             sensor=sensors[3], location=locations[3], timestamp=timestamps[1]),
#         SensorData(
#             sensor=sensors[4], location=locations[4], timestamp=timestamps[2]),
#     ])

#     SensorDataValue.objects.bulk_create([
#         SensorDataValue(
#             sensordata=sensordata[0], value="4", value_type="P2"),
#         SensorDataValue(
#             sensordata=sensordata[1], value="4", value_type="P1"),
#         # Won't be tracked as last active
#         SensorDataValue(
#             sensordata=sensordata[2], value="4", value_type="Temp"),
#     ])

#     from django.core.management import call_command

#     call_command("cache_lastactive_nodes")

#     return timestamps
