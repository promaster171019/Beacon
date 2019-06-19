from django.core.management.base import BaseCommand
from classapp.models import StudentConference


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for obj in StudentConference.objects.all():
            obj.staff = obj.event.created_by
            obj.save()
        self.stdout.write('Finished')
