from django.core.management.base import BaseCommand

from students.models import Student, StudentStatus
from beaconapp.models import BreakTime, DiscontinuationForm


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        new_status = StudentStatus.objects.filter(status='New Student').first()
        bf_pending_status = StudentStatus.objects.filter(status='Break Pending').first()
        ds_pending_status = StudentStatus.objects.filter(status='Discontinuation Pending').first()

        # set new status for the students
        for student in Student.objects.filter():
            student.status = new_status
            student.save()

        # set the pending status for the break form student
        for form in BreakTime.objects.filter():
            if form.student:
                form.student.status = bf_pending_status
                form.student.save()

        # set the pending status for the discontinuation form student
        for form in DiscontinuationForm.objects.filter():
            if form.student:
                form.student.status = ds_pending_status
                form.student.save()

        self.stdout.write('Finished')
