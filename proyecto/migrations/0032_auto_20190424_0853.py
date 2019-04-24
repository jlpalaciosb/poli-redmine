# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-24 12:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0031_remove_campopersonalizado_campo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstory',
            name='criterioAceptacion',
            field=models.CharField(help_text='condiciones para que el US sea aceptado como terminado', max_length=500, verbose_name='criterio de aceptación'),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='tiempoEjecutado',
            field=models.FloatField(default=0, verbose_name='tiempo ejecutado (en horas)'),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='tiempoPlanificado',
            field=models.IntegerField(help_text='cuántas horas cree que le llevará a una persona terminar este US', verbose_name='tiempo planificado (en horas)'),
        ),
    ]
