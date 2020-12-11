import os
import requests

def get_droplets():
    url = 'https://api.purpleair.com/v1'
    r = requests.get(url, headers={'Authorization':'Bearer %s' % 'access_token'})
    droplets = r.json()
    droplet_list = []
    for i in range(len(droplets['droplets'])):
        droplet_list.append(droplets['droplets'][i])
    return droplet_list