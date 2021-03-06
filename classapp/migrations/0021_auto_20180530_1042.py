# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-05-30 10:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0020_auto_20180517_0527'),
    ]

    operations = [
        migrations.AddField(
            model_name='classdefinition',
            name='duration',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='class_definition_duration', to='classapp.ClassDuration'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='classdefinition',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='class_definition_location', to='classapp.Location'),
        ),
    ]
