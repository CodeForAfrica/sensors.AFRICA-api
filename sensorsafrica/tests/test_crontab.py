import crontab
from django.core.management import call_command


class TestSensorDataPushFull:
    def test_crontab_intalled(self):
        call_command("cron", dokku_appname="sensorsafrica-test", breadcrumb="sensorsafrica-test")

        tab = crontab.CronTab(user=True)

        count = len(list(tab.find_comment("sensorsafrica-test")))

        assert count == 1
