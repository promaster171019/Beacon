# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-13 10:39
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=100, verbose_name='Book short name')),
                ('long_name', models.CharField(max_length=200, verbose_name='Book long name')),
                ('total_score', models.PositiveIntegerField(verbose_name='Total score')),
                ('max_weeks_1_hour', models.PositiveIntegerField(null=True, verbose_name='Max weeks 1 hour')),
                ('max_weeks_2_hour', models.PositiveIntegerField(null=True, verbose_name='Max weeks 2 hour')),
            ],
        ),
        migrations.CreateModel(
            name='BookExam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(verbose_name='Student score for book')),
                ('total_score', models.FloatField(verbose_name='Total score for book')),
            ],
        ),
        migrations.CreateModel(
            name='BooksGiven',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('modified_date', models.DateTimeField(auto_now=True, verbose_name='Created date')),
            ],
        ),
        migrations.CreateModel(
            name='ClassDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Start class date')),
                ('end_date', models.DateField(verbose_name='End class date')),
                ('max_capacity', models.SmallIntegerField(null=True, verbose_name='Max number of students')),
                ('weekday', models.CharField(max_length=20, null=True, verbose_name='Weekday')),
                ('gc_event_id', models.CharField(max_length=200, null=True, verbose_name='Google Calendar Id')),
            ],
        ),
        migrations.CreateModel(
            name='ClassDuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ClassRollout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_capacity', models.PositiveIntegerField(verbose_name='Max capacity of class')),
                ('class_status', models.CharField(max_length=200, verbose_name='Class status')),
                ('start_time', models.TimeField(verbose_name='Start time')),
                ('end_time', models.TimeField(verbose_name='End time')),
                ('class_date', models.DateField(verbose_name='Class date')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
                ('replacement_rollout', models.CharField(max_length=200, null=True)),
                ('comments', models.CharField(max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=100, verbose_name='Book short name')),
                ('long_name', models.CharField(max_length=100, verbose_name='Book short name')),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_name', models.CharField(max_length=20, verbose_name='Grade name')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=40, verbose_name='Short name')),
                ('long_name', models.CharField(max_length=200, verbose_name='Long name')),
                ('street', models.CharField(max_length=200, null=True, verbose_name='Street')),
                ('city', models.CharField(max_length=200, null=True, verbose_name='City')),
                ('state', models.CharField(max_length=200, null=True, verbose_name='State')),
                ('zip', models.CharField(max_length=20, null=True, verbose_name='Zip code')),
                ('calendarId', models.CharField(max_length=200, null=True, verbose_name='Google Calendar ID')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_no', models.PositiveSmallIntegerField(verbose_name='Room number')),
                ('room_name', models.CharField(max_length=200, verbose_name='Room name')),
            ],
        ),
        migrations.CreateModel(
            name='StudentConference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.BooleanField(default=False)),
                ('notes', models.TextField(null=True, verbose_name='Comments/Notes')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vacation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Vacation date')),
                ('vacation_name', models.CharField(max_length=200, verbose_name='Vacation name')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='Created date')),
            ],
        ),
    ]
