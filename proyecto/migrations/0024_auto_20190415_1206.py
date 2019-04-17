# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-15 16:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0023_auto_20190415_1012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actividad',
            old_name='us_sprint',
            new_name='usSprint',
        ),
        migrations.AlterField(
            model_name='actividad',
            name='descripcion',
            field=models.CharField(max_length=500, verbose_name='descripción'),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='estado',
            field=models.CharField(choices=[('TODO', 'To Do'), ('DOING', 'Doing'), ('DONE', 'Done')], default='DOING', max_length=10),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='horasTrabajadas',
            field=models.IntegerField(default=0, verbose_name='horas trabajadas'),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='responsable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyecto.MiembroSprint'),
        ),
    ]