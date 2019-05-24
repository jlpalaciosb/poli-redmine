# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-23 22:46
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import proyecto.models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0055_auto_20190523_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='diasHabiles',
            field=models.PositiveIntegerField(default=6, help_text='cantidad de días hábiles en la semana', validators=[proyecto.models.validar_mayor_a_cero, django.core.validators.MaxValueValidator(limit_value=7)], verbose_name='días hábiles'),
        ),
    ]