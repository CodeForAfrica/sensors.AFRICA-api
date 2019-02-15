import shelve
import uuid
import crontab
from django.core.management import BaseCommand


class Command(BaseCommand):

    help = "Install or reinstall cronjobs"

    def add_arguments(self, parser):
        parser.add_argument("--breadcrumb", default=str(uuid.uuid4()))
        parser.add_argument("--dokku_appname", default=False)
        parser.add_argument("--clear", default=False)

    def handle(self, *args, **options):
        tab = crontab.CronTab(user=True)

        breadcrumb = options["breadcrumb"]
        dokku_appname = options["dokku_appname"]
        clear = options["clear"]

        if not dokku_appname and not clear:
            return

        with shelve.open("crons") as db:
            if "breadcrumb" in db.keys():
                previous_breadcrumb = db["breadcrumb"]

                count = len(list(tab.find_comment(previous_breadcrumb)))

                if count:
                    tab.remove_all(comment=previous_breadcrumb)
                    tab.write()

            if dokku_appname:
                tab.new(
                    command="dokku enter {dokku_appname} web python3 manage.py calculate_data_statistics >> /var/log/cron.log 2>&1".format(
                        dokku_appname=dokku_appname
                    ),
                    comment=breadcrumb,
                ).setall("0 * * * *")

                tab.write()

                db["breadcrumb"] = breadcrumb
        print(tab.render())
