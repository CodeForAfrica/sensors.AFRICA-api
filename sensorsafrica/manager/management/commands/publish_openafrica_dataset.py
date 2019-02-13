import os

import ckanapi
import requests
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        openAFRICA_API_KEY = os.environ.get("openAFRICA_API_KEY")
        openAFRICA_URL = "https://africaopendata.org"
        folder = os.environ.get("ARCHIVE_FOLDER_PATH", "/opt/code/archive")

        ckan = ckanapi.RemoteCKAN(openAFRICA_URL, apikey=openAFRICA_API_KEY)

        package = ckan.action.package_show(id="sensorsafrica-airquality-archive")
        resources = package["resources"]

        for subfolder in os.listdir(folder):
            path = os.path.join(folder, subfolder)
            for filename in os.listdir(path):
                path = os.path.join(path, filename)
                extension = os.path.splitext(filename)[1][1:].upper()

                resource_name = filename.replace("_", " ").replace(".", " ").upper()

                resource = list(filter(lambda resource: resource["name"] == resource_name, resources))
                if resource:
                    resource = ckan.action.resource_update(
                        id=resource[0]["id"],
                        url="upload",
                        upload=open(path),
                    )
                else:
                    resource = ckan.action.resource_create(
                        package_id=package["id"],
                        name=resource_name,
                        format=extension,
                        url="upload",
                        upload=open(path),
                    )
