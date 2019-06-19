from django.core.management.base import BaseCommand

from students.models import StudentInClass


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        for obj in StudentInClass.objects.all().exclude(status__in=['cancelled', 'scheduled']):
            obj.status = 'scheduled'
            obj.save()

        self.stdout.write('Finished')