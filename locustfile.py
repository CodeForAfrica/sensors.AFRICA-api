import json
import os
import random
from locust import HttpLocust, TaskSet, task, events


sensor_count = 0

class SensorBehavior(TaskSet):
    def on_start(self):
        # Fake Sensor Node UID
        self.SENSOR = 'fake-%d' % sensor_count
        sensor_count += 1
            
    @task
    def push_data(self):
        payload = {
            "sensordatavalues": [
                { "value_type": "P1", "value": str(random.randrange(1,20)) },
                { "value_type": "P2", "value": str(random.randrange(1,20)) },
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "PIN": "1", # always going to test using pin 1 for fake sensor
            "SENSOR": self.SENSOR 
        }
        self.client.post(
            "/v1/push-sensor-data/",
            headers=headers,
            data=json.dumps(payload)
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
