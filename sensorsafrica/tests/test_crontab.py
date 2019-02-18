from crontab import CronTab
from django.core.management import call_command

import unittest

from unittest import mock

crontab = CronTab(user=True)


def get_crontab(*args, **kwargs):
    return crontab



@mock.patch("crontab.CronTab", autospec=True, side_effect=get_crontab)
class TestCronCommand(unittest.TestCase):
    def test_crontab_intalled(self, _):
        call_command("cron", dokku_appname="sensorsafrica-test")

        count = len(list(crontab.find_comment("sensorsafrica-test")))

        assert count == 1

    def test_crontab_reintalled(self, _):
        call_command("cron", dokku_appname="sensorsafrica-test")

        count = len(list(crontab.find_comment("sensorsafrica-test")))

        assert count == 1

        call_command("cron", dokku_appname="sensorsafrica-test-reinstall")

        prev_jobs = len(list(crontab.find_comment("sensorsafrica-test")))
        current_jobs = len(list(crontab.find_comment("sensorsafrica-test-reinstall")))

        assert prev_jobs == 0
        assert current_jobs == 1

    def test_crontab_clear(self, _):
        call_command("cron", clear=True)

        prev_jobs = len(list(crontab.find_comment("sensorsafrica-test")))
        current_jobs = len(list(crontab.find_comment("sensorsafrica-test-reinstall")))

        assert prev_jobs == 0
        assert current_jobs == 0
