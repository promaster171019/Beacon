from django.core.management.base import BaseCommand
from parents.models import Parent


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for obj in Parent.objects.all():

            if obj.home_phone == '':
                obj.home_phone = None

            if obj.alternate_phone == '':
                obj.alternate_phone = None

            if obj.cell_phone == '':
                obj.cell_phone = None

            obj.save()
        self.stdout.write('Finished')
