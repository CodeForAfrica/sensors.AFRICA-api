import json
import os
import random
from locust import HttpLocust, TaskSet, task

# Don't run SensorBehaviour on production server
class SensorBehavior(TaskSet):
    @task(1)
    def push_data(self):
        payload = {
            "sensordatavalues": [
                {"value_type": "P1", "value": str(random.randrange(1,20))},
                {"value_type": "P2", "value": str(random.randrange(1,20))},
            ]
        }
        headers = {
            "content-type": "application/json",
            "PIN": "1",
            "SENSOR": "esp8266-1837609",
            "token": os.environ.get("SENSORSAFRICA_API_TOKEN"),
        }
        self.client.post(
            "/v1/push-sensor-data"
        )


class UserBehavior(TaskSet):
    @task(10)
    def air_data_filter_supported_city(self):
        with self.client.get("/v2/cities", catch_response=True) as response:
            results = response.json()
            for city in results["results"]:
                self.client.get("/v2/data/air?city=%s" % city["slug"])

    @task(1)
    def air_data(self):
        self.client.get("/v2/data/air")


class APIUser(HttpLocust):
    weight = 1 # 
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000


class Sensor(HttpLocust):
    weight = 2 # Sensors should more likely be interacting with the api
    task_set = SensorBehavior
    min_wait = 60000
    max_wait = 65000
