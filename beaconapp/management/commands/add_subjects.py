from django.core.management.base import BaseCommand

from students.models import Student, StudentInClass


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        for obj in Student.objects.all():
            sic = StudentInClass.objects.filter(student=obj).first()
            if(sic and sic.class_id):
                obj.subjects.add(sic.class_id.subject)
                obj.save()

        self.stdout.write('Finished')