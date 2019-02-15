from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Seed the created database"

    def handle(self, *args, **options):
        call_command("loaddata", "auth.json")
        call_command("loaddata", "sensortypes.json")
        call_command("loaddata", "sensors.json")
        call_command("loaddata", "sensordata.json")
