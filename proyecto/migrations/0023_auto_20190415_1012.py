# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-04-15 14:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0022_auto_20190414_2252'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiembroSprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('horasAsignadas', models.IntegerField(verbose_name='Horas asignadas al miembro')),
                ('miembro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyecto.MiembroProyecto', verbose_name='Miembro del Sprint')),
                ('sprint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyecto.Sprint', verbose_name='Sprint')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='miembrosprint',
            unique_together=set([('miembro', 'sprint')]),
        ),
    ]