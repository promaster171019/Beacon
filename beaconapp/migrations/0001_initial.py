# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-13 10:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BreakTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create date')),
                ('date_off', models.DateField(verbose_name='Date off')),
                ('start_time', models.DateField(verbose_name='Start break date')),
                ('end_time', models.DateField(verbose_name='End break date')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='break_event', to='beaconapp.Timeline')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='break_staff', to='staff.Staff')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='break_student', to='students.Student')),
                ('subjects', models.CharField(default='', max_length=200, null=True, verbose_name='Subjects')),
                ('reason', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='DiscontinuationForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200, verbose_name='Subjects')),
                ('start_date', models.CharField(max_length=200, verbose_name='Date of Discontinuation')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='discontinuation_form',
                                            to='beaconapp.Timeline')),
                ('reason', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Pdf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='PDF name')),
                ('type', models.CharField(max_length=100, verbose_name='PDF type')),
                ('file', models.FileField(upload_to='media/protected/pdf')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create date')),
                ('pdf', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                          related_name='timeline_event',
                                          to='beaconapp.Timeline', verbose_name='Timeline event')),
            ],
        ),
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100, verbose_name='Type')),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create date')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.Staff', verbose_name='Created by')),
                ('staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                            related_name='staff_timeline',
                                            to='staff.Staff', verbose_name='Staff timeline')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                              related_name='student_timeline',
                                              to='students.Student', verbose_name='Student timeline')),

            ],
        ),
        migrations.CreateModel(
            name='UpgradeForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200, verbose_name='Subjects')),
                ('start_date', models.CharField(max_length=200, verbose_name='Upgrade Date')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upgrade_form', to='beaconapp.Timeline')),
            ],
        ),
    ]