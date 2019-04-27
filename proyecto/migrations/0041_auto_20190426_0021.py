# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-26 04:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0040_auto_20190425_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstorysprint',
            name='asignee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proyecto.MiembroSprint', verbose_name='Encargado'),
        ),
        migrations.AlterField(
            model_name='userstorysprint',
            name='us',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyecto.UserStory', verbose_name='User Story'),
        ),
    ]
