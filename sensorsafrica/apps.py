from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'sensorsafrica.api.accounts'


class SensorsConfig(AppConfig):
    name = 'sensorsafrica.api.sensors'
    # This is to not conflict with feinstaub sensors app label
    label = 'sensorsafrica.sensors'
