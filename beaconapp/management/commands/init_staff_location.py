from django.core.management.base import BaseCommand

from classapp.models import Location
from staff.models import Staff


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        default_location = Location.objects.filter(short_name='EB').first()

        for obj in Staff.objects.filter():
            obj.locations.add(default_location)
            obj.save()

        self.stdout.write('Finished')
