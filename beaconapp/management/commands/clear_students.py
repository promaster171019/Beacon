from django.core.management.base import BaseCommand
from students.models import Student


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for obj in Student.objects.filter():
            if not obj.parents.count():
                print("stundet - {}".format(obj.id))
                obj.delete()
        self.stdout.write('Finished')
