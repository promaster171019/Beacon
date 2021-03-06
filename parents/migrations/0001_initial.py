# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-13 10:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200, verbose_name='First name')),
                ('last_name', models.CharField(max_length=200, verbose_name='Last name')),
                ('cell_phone', models.CharField(max_length=20, null=True, verbose_name='Cell phone')),
                ('home_phone', models.CharField(max_length=20, null=True, verbose_name='Home phone')),
                ('alternate_phone', models.CharField(max_length=200, verbose_name='Alternate phone')),
                ('email', models.CharField(max_length=50, null=True, verbose_name='Email')),
                ('photo', models.FileField(null=True, upload_to='media/photos', verbose_name='Photo')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='Create date')),
                ('modified_date', models.DateField(auto_now_add=True, null=True, verbose_name='Modified date')),
                ('profession', models.CharField(max_length=100, null=True, verbose_name='Profession')),
                ('race', models.CharField(max_length=200, null=True, verbose_name='Race')),
                ('homeowner_renter', models.CharField(max_length=200, null=True, verbose_name='Homeowner renter')),
                ('persona', models.CharField(max_length=200, null=True, verbose_name='Persona')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_created_by', to='staff.Staff', verbose_name='Created by')),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_modified_by', to='staff.Staff', verbose_name='Modified by')),
            ],
        ),
    ]
