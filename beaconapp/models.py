import os

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from staff.models import Staff
from students.models import Student
from parents.models import Parent


class Timeline(models.Model):
    type = models.CharField('Type', max_length=100)
    title = models.CharField('Title', max_length=200)
    description = models.TextField('Description')
    student = models.ForeignKey(Student, verbose_name='Student timeline',
                                related_name='student_timeline', null=True)
    staff = models.ForeignKey(Staff, verbose_name='Staff timeline',
                              related_name='staff_timeline', null=True)
    created_by = models.ForeignKey(Staff, verbose_name='Created by')
    create_date = models.DateTimeField('Create date', default=timezone.now)

    def __str__(self):
        return '{} {}'.format(self.title, self.type)

    def get_timeline(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_by": '{} {}'.format(self.created_by.user.first_name, self.created_by.user.last_name),
            "created_date": self.create_date.strftime('%m/%d/%Y'),
            "created_time": self.create_date.strftime('%H:%M'),
            "type": self.type,
            "note": {'text': self.timeline_event_conference.first().notes},
            "pdfs": []
        }

    @property
    def data(self):
        return {
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'student': self.student.id,
            'staff': self.staff.id,
            'event': self.event.id,
            'material': self.material.id
        }


class Pdf(models.Model):
    name = models.CharField('PDF name', max_length=200)
    type = models.CharField('PDF type', max_length=100)
    file = models.FileField(upload_to='media/protected/pdf')
    create_date = models.DateTimeField('Create date', default=timezone.now)
    event = models.ForeignKey(Timeline, verbose_name="Timeline event",
                              related_name='timeline_event', null=True)

    def __str__(self):
        return self.name

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    @property
    def pretty_name(self):
        return "{0}{1}".format(
            slugify(self.name),
            self.extension()
        )


class BreakTime(models.Model):
    create_date = models.DateTimeField('Create date', default=timezone.now)
    date_off = models.DateField("Date off")
    start_time = models.DateField("Start break date")
    end_time = models.DateField("End break date")
    subjects = models.CharField('Subjects', max_length=200, default='', null=True)
    event = models.ForeignKey(Timeline, related_name='break_event')
    student = models.ForeignKey(Student, related_name='break_student')
    staff = models.ForeignKey(Staff, related_name='break_staff')
    parent = models.ForeignKey(Parent, related_name='break_parent', null=True)
    reason = models.TextField(null=True)

    def __str__(self):
        return 'Break form'

# pre_save.connect(timezone_pre_save, sender=BreakTime)


class DiscontinuationForm(models.Model):
    subject = models.CharField('Subjects', max_length=200)
    start_date = models.CharField('Date of Discontinuation', max_length=200)
    event = models.ForeignKey(Timeline, related_name='discontinuation_form')
    student = models.ForeignKey(Student, related_name='discontinuation_student', null=True)
    staff = models.ForeignKey(Staff, related_name='discontinuation_staff', null=True)
    parent = models.ForeignKey(Parent, related_name='discontinuation_parent', null=True)
    reason = models.TextField(null=True)

    def __str__(self):
        return 'Discontinuation form'


class UpgradeForm(models.Model):
    subject = models.CharField('Subjects', max_length=200)
    start_date = models.CharField('Upgrade Date', max_length=200)
    event = models.ForeignKey(Timeline, related_name='upgrade_form')
    student = models.ForeignKey(Student, related_name='upgrade_student', null=True)
    staff = models.ForeignKey(Staff, related_name='upgrade_staff', null=True)
    parent = models.ForeignKey(Parent, related_name='upgrade_parent', null=True)
    duration = models.CharField('Duration', max_length=200, default='1 on 1')
    payment_method = models.CharField('Payment Method', max_length=200, null=True)
    notes = models.TextField(null=True)

    def __str__(self):
        return 'Upgrade form'
