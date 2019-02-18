import shelve
import uuid
import crontab
from django.core.management import BaseCommand


class Command(BaseCommand):

    help = "Install or reinstall cronjobs"

    def add_arguments(self, parser):
        parser.add_argument("--dokku_appname", default=False)
        parser.add_argument("--clear", default=False)
        parser.add_argument("--log", default="/var/log/cron.log")

    def handle(self, *args, **options):
        tab = crontab.CronTab(user=True)
        dokku_appname = options["dokku_appname"]
        clear = options["clear"]
        log = options["log"]

        if not dokku_appname and not clear:
            return

        with shelve.open("crons") as db:
            if "breadcrumb" in db.keys():
                breadcrumb = db["breadcrumb"]

                count = len(list(tab.find_comment(breadcrumb)))

                if count:
                    tab.remove_all(comment=breadcrumb)
                    tab.write()

            if dokku_appname and not clear:
                tab.new(
                    command="dokku enter {dokku_appname} web python3 manage.py calculate_data_statistics >> {log} 2>&1".format(
                        dokku_appname=dokku_appname, log=log
                    ),
                    comment=dokku_appname,
                ).setall("*/10 * * * *")

                tab.write()

                db["breadcrumb"] = dokku_appname
        print(tab.render())
