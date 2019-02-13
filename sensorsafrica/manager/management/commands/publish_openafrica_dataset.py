import os

import ckanapi
import requests
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        openAFRICA_API_KEY = os.environ.get("openAFRICA_API_KEY")
        openAFRICA_URL = "https://africaopendata.org"
        ckan = ckanapi.RemoteCKAN(openAFRICA_URL, apikey=openAFRICA_API_KEY)
        package_name = "sensors.AFRICA Air Quality Archive"
        package_title = "sensors.AFRICA Air Quality Archive"
        folder = "/opt/code/archive"

        try:
            package = ckan.action.package_create(name=package_name, title=package_title)
        except ckanapi.ValidationError as e:
            if e.error_dict["__type"] == "Validation Error" and (
                e.error_dict["name"] == ["That URL is already in use."]
            ):
                package = ckan.action.package_show(id=package_name)
            else:
                raise

        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            extension = os.path.splitext(filename)[1][1:].upper()
            resource_name = "sensors.AFRICA Air Quality Data {extension}".format(
                extension=extension
            )
            r = requests.post(
                openAFRICA_URL + "/api/action/resource_create",
                data={
                    "package_id": package["id"],
                    "name": resource_name,
                    "format": extension,
                    "url": "upload",
                },
                headers={"Authorization": openAFRICA_API_KEY},
                files=[("upload", open(path))],
            )

            if r.status_code != 200:
                print("Error while creating resource: {0}".format(r.content))
                break
