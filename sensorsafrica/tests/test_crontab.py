import crontab
from django.core.management import call_command


class TestSensorDataPushFull:
    def test_crontab_intalled(self):
        call_command("cron", dokku_appname="sensorsafrica-test", breadcrumb="sensorsafrica-test")

        tab = crontab.CronTab(user=True)

        count = len(list(tab.find_comment("sensorsafrica-test")))

        assert count == 1

    def test_crontab_reintalled(self):
        call_command("cron", dokku_appname="sensorsafrica-test-reinstall", breadcrumb="sensorsafrica-test-reinstall")

        tab = crontab.CronTab(user=True)

        prev_jobs = len(list(tab.find_comment("sensorsafrica-test")))
        current_jobs = len(list(tab.find_comment("sensorsafrica-test-reinstall")))

        assert prev_jobs == 0
        assert current_jobs == 1

    def test_crontab_clear(self):
        call_command("cron", clear=True)

        tab = crontab.CronTab(user=True)

        prev_jobs = len(list(tab.find_comment("sensorsafrica-test")))
        current_jobs = len(list(tab.find_comment("sensorsafrica-test-reinstall")))

        assert prev_jobs == 0
        assert current_jobs == 0
