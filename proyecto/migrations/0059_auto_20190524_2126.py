# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-25 01:26
from __future__ import unicode_literals

from django.db import migrations, models
import proyecto.models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0058_auto_20190524_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='duracionSprint',
            field=models.PositiveIntegerField(default=1, help_text='duración estimada para los sprints (en semanas)', validators=[proyecto.models.validar_mayor_a_cero], verbose_name='duración del sprint'),
        ),
    ]