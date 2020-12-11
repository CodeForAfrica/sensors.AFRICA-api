import os
import requests

def get_sensors():
    query = {'fields':'sensor_index'}
    url = 'https://api.purpleair.com/v1/sensors?fields=sensor_index'
    r = requests.get(url, params=query, headers={'Authorization':'Bearer %s' % 'access_token'})
    results = r.json()
    sensors_id_list = []
    for i in range(len(results.data)):
        sensors_id_list.append(results.data[i])
    return sensors_id_list