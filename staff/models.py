from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cell_phone = models.CharField('Phone', max_length=20)
    personal_email = models.CharField('Personal email', null=True, max_length=50)
    street = models.CharField('Street', null=True, max_length=200)
    city = models.CharField('City', null=True, max_length=200)
    zip = models.CharField('Zip code', null=True, max_length=20)
    hire_date = models.DateField('Hire date', null=True)
    date_of_birth = models.DateField('Date of birth', null=True)
    referred_by_staff_id = models.PositiveIntegerField('Reffered by', null=True)
    photo = models.TextField('Photo', null=True, blank=True)
    admin_flag = models.BooleanField('Is admin', default=False)
    manager_flag = models.BooleanField('Is manager', default=False)
    teacher_flag = models.BooleanField('Is teacher', default=True)
    active = models.BooleanField('Is active', default=True)
    subjects = models.ManyToManyField('classapp.Subject', related_name='staff_subjects')
    locations = models.ManyToManyField('classapp.Location', related_name='staff_locations')
    default_location = models.ForeignKey('classapp.Location', null=True)

    def __str__(self):
        return "{}".format(self.user.username)

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def full_name(self):
        return '{} {}'.format(
            self.user.first_name.capitalize(),
            self.user.last_name.capitalize()
        )

    def get_locations(self):
        return [location.short_name for location in self.locations.all()]

    def get_role(self):
        if self.admin_flag:
            return 'admin'
        elif self.manager_flag:
            return 'manager'
        else:
            return 'teacher'


class StaffNote(models.Model):
    staff = models.ForeignKey(Staff, verbose_name='Staff', related_name='staff_note')
    note = models.TextField('Note text')
    note_type = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(Staff, verbose_name='Created by',
                                   related_name='staff_note_created_by')
    create_date = models.DateTimeField('Created date', default=timezone.now)
    modified_by = models.ForeignKey(Staff, verbose_name='Modified by',
                                    related_name='staff_note_modified_by', null=True)
    modified_date = models.DateTimeField('Modified date', default=timezone.now, null=True)
    event = models.ForeignKey('beaconapp.Timeline', related_name='staff_note_event')


class Token(models.Model):
    user = models.OneToOneField(User)
    token = models.CharField(max_length=2000)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return "{} token".format(self.user)
