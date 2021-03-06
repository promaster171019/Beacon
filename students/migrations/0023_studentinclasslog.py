# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-08 04:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0027_staff_locations'),
        ('students', '0022_auto_20180808_0405'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentInClassLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=200, null=True, verbose_name='Status')),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Created date')),
                ('class_instance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_in_class_log', to='students.StudentInClass', verbose_name='Student in class')),
                ('staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.Staff', verbose_name='Created by')),
            ],
        ),
    ]
