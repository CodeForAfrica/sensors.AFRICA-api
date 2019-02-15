import crontab
from django.core.management import BaseCommand

BREADCRUMB = "sensorsafrica"


class Command(BaseCommand):

    help = "Install or reinstall cronjobs"

    def add_arguments(self, parser):
        parser.add_argument("--breadcrumb")

    def handle(self, *args, **options):
        tab = crontab.CronTab(user=True)

        breadcrumb = options["breadcrumb"]

        count = len(list(tab.find_comment(breadcrumb)))

        if count:
            tab.remove_all(comment=breadcrumb)
            tab.write()

        tab.new(
            command="dokku enter sensorsafrica-staging web python3 manage.py calculate_data_statistics >> /var/log/cron.log 2>&1",
            comment=breadcrumb,
        ).setall("0 * * * *")
        tab.write()

        print(tab.render())
