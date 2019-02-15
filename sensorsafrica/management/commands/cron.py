import crontab
from django.core.management import BaseCommand

BREADCRUMB = "sensorsafrica"


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        tab = crontab.CronTab(user=True)

        count = len(list(tab.find_comment(BREADCRUMB)))

        if count:
            tab.remove_all(comment=BREADCRUMB)
            tab.write()

        tab.new(
            "dokku enter sensorsafrica-staging web python3 manage.py calculate_data_statistics >> /var/log/cron.log 2>&1",
            BREADCRUMB,
        ).setall("0 * * * *")
        tab.write()

        print(tab.render())
