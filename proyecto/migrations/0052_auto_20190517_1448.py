# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-17 18:48
from __future__ import unicode_literals

from django.db import migrations, models
import proyecto.models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0051_auto_20190517_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='actividad',
            name='dia_sprint',
            field=models.PositiveIntegerField(help_text='La cantidad de dias que pasaron desde que inicio el sprint hasta que se cargo esta actividad', null=True),
        ),
        migrations.AddField(
            model_name='sprint',
            name='cant_dias_habiles',
            field=models.PositiveIntegerField(default=6, help_text='La cantidad de dias habiles tomando al lunes como el dia inicial', verbose_name='Cantidad de dias habiles'),
        ),
        migrations.AddField(
            model_name='userstorysprint',
            name='prioridad_suprema',
            field=models.BooleanField(default=False, help_text='Campo que determina si un user story no culmino en un sprint anterior'),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='diasHabiles',
            field=models.PositiveIntegerField(default=6, help_text='cantidad de días hábiles en la semana', validators=[proyecto.models.validar_mayor_a_cero], verbose_name='días hábiles'),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='duracionSprint',
            field=models.PositiveIntegerField(default=2, help_text='duración estimada para los sprints (en semanas)', validators=[proyecto.models.validar_mayor_a_cero], verbose_name='duración del sprint'),
        ),
    ]