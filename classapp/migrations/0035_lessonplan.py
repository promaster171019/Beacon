# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-11-29 06:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0034_classrollout_show_while_cancelled'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.PositiveIntegerField(null=True, verbose_name='Week')),
                ('cw', models.CharField(max_length=256, verbose_name='Classwork')),
                ('hw', models.CharField(max_length=256, verbose_name='Homework')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_plan_book', to='classapp.Book', verbose_name='Book in lesson plan')),
            ],
        ),
    ]
