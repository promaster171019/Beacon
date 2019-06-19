from datetime import timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand

from students.models import Student, StudentStatus
from beaconapp.models import BreakTime, DiscontinuationForm
from beaconapp.utils import convert_to_date


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        new_status = StudentStatus.objects.filter(status='New Student').first()
        active_status = StudentStatus.objects.filter(status='Active').first()
        bf_pending_status = StudentStatus.objects.filter(status='Break Pending').first()
        bf_progress_status = StudentStatus.objects.filter(status='On Break').first()
        ds_pending_status = StudentStatus.objects.filter(status='Discontinuation Pending').first()
        ds_progress_status = StudentStatus.objects.filter(status='Discontinued').first()
        today = timezone.now()
        today_date = today.date()

        # set active status for the new students
        for student in Student.objects.filter(status=new_status):
            if (student.create_date + timedelta(days=120)) <= today:
                student.status = active_status
                student.save()

        # set the progress status if the break is started
        for form in BreakTime.objects.filter():
            end = form.end_time
            start = form.start_time
            student = form.student

            if student:
                if end >= today_date >= start and student.status is bf_pending_status:
                    student.status = bf_progress_status
                    student.save()

                # if today_date > end and student.status is bf_progress_status:
                #     student.status = active_status
                #     student.save()

        # set the progress status if the discontinuation is started
        for form in DiscontinuationForm.objects.filter():
            start = convert_to_date(form.start_date)
            student = form.student

            if today >= start and student and student.status is ds_pending_status:
                student.status = ds_progress_status
                student.save()

        self.stdout.write('Finished')
