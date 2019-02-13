import os
from urllib import request

import boto3
import ckanapi
from django.core.management import BaseCommand
import time


class Command(BaseCommand):
    help = ""

    def add_arguments(self, parser):
        parser.add_argument("--from_s3")

    def handle(self, *args, **options):
        openAFRICA_API_KEY = os.environ.get("openAFRICA_API_KEY")
        openAFRICA_URL = "https://africaopendata.org"

        ckan = ckanapi.RemoteCKAN(openAFRICA_URL, apikey=openAFRICA_API_KEY)

        package = ckan.action.package_show(id="sensorsafrica-airquality-archive")
        resources = package["resources"]

        if options.get("from_s3"):
            bucket = self._s3_archive_bucket()

            for obj in bucket.objects.all():
                filename = obj.key.split("/")[-1]

                region = os.environ.get("AWS_REGION")
                bucket_name = os.environ.get("AWS_BUCKET_NAME")
                url = "http://s3-%s.amazonaws.com/%s/%s" % (
                    region,
                    bucket_name,
                    obj.key,
                )

                self.create_or_update_resource(
                    filename, resources, ckan, request.urlopen(url), package
                )

                time.sleep(5)
        else:
            folder = os.environ.get("ARCHIVE_FOLDER_PATH", "/opt/code/archive")

            for subfolder in os.listdir(folder):
                path = os.path.join(folder, subfolder)
                for filename in os.listdir(path):
                    path = os.path.join(path, filename)

                    self.create_or_update_resource(
                        filename, resources, ckan, open(path), package
                    )

    def create_or_update_resource(self, filename, resources, ckan, upload, package):
        extension = os.path.splitext(filename)[1][1:].upper()

        resource_name = filename.replace("_", " ").replace(".", " ").upper()

        resource = list(
            filter(lambda resource: resource["name"] == resource_name, resources)
        )
        if resource:
            resource = ckan.action.resource_update(
                id=resource[0]["id"], url="upload", upload=upload
            )
        else:
            resource = ckan.action.resource_create(
                package_id=package["id"],
                name=resource_name,
                format=extension,
                url="upload",
                upload=upload,
            )

    @staticmethod
    def _s3_archive_bucket():
        bucket_name = os.environ.get("AWS_BUCKET_NAME")
        access_key = os.environ.get("AWS_ACCESS_KEY")
        secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = os.environ.get("AWS_REGION")

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )
        s3 = session.resource("s3")

        bucket = s3.Bucket(bucket_name)

        return bucket
