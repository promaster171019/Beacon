# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-12-26 06:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classapp', '0043_auto_20181219_0225'),
        ('students', '0034_studentinclass_status_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinclass',
            name='c_book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='c_students_for_book', to='classapp.Book'),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_classwork',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_finished_classwork',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_finished_homework',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_fixups_done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_homework',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_mentals',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_next_lesson_plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='c_future_students', to='classapp.LessonPlan'),
        ),
        migrations.AddField(
            model_name='studentinclass',
            name='c_selected_lesson_plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='c_current_students', to='classapp.LessonPlan'),
        ),
    ]
