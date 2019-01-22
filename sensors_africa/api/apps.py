from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'api.accounts'

class SensorsConfig(AppConfig):
    name = 'api.sensors'
    # This is to not conflict with feinstaub sensors app label
    label = 'sensors_africa.sensors'
