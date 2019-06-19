from django.db import models
from django.utils import timezone

from staff.models import Staff


class Parent(models.Model):
    first_name = models.CharField('First name', max_length=200, null=True, blank=True)
    last_name = models.CharField('Last name', max_length=200, null=True, blank=True)
    cell_phone = models.CharField('Cell phone', max_length=20, null=True, blank=True)
    home_phone = models.CharField('Home phone', max_length=20, null=True, blank=True)
    alternate_phone = models.CharField('Alternate phone', max_length=200, null=True)
    email = models.CharField('Email', max_length=50, null=True, blank=True)
    photo = models.TextField('Photo', null=True, blank=True)
    profession = models.CharField('Profession', max_length=100, null=True)
    race = models.CharField('Race', max_length=200, null=True)
    homeowner_renter = models.CharField('Homeowner renter', max_length=200, null=True)
    persona = models.CharField('Persona', max_length=200, null=True)
    notification = models.BooleanField(default=False)

    create_date = models.DateTimeField('Create date', default=timezone.now)
    created_by = models.ForeignKey(Staff, related_name='parent_created_by',
                                   verbose_name='Created by')

    modified_date = models.DateTimeField('Modified date', default=timezone.now, null=True)
    modified_by = models.ForeignKey(Staff, related_name='parent_modified_by',
                                    verbose_name='Modified by', null=True)

    @property
    def full_name(self):
        return "{} {}".format(self.first_name.capitalize(), self.last_name.capitalize())

    def __str__(self):
        return self.full_name
