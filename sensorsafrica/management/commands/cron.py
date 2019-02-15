import crontab
import os
from django.core.management import BaseCommand


class Command(BaseCommand):

    help = "Install or reinstall cronjobs"

    def add_arguments(self, parser):
        parser.add_argument("--breadcrumb")
        parser.add_argument("--dokku_appname")

    def handle(self, *args, **options):
        tab = crontab.CronTab(user=True)

        breadcrumb = options["breadcrumb"]
        dokku_appname = options["dokku_appname"]

        count = len(list(tab.find_comment(breadcrumb)))

        if count:
            tab.remove_all(comment=breadcrumb)
            tab.write()

        tab.new(
            command="dokku enter {dokku_appname} web python3 manage.py calculate_data_statistics >> /var/log/cron.log 2>&1".format(dokku_appname=dokku_appname),
            comment=breadcrumb,
        ).setall("0 * * * *")
        tab.write()

        print(tab.render())
