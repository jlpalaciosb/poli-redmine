# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-08 14:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proyecto', '0047_auto_20190507_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='justificacion',
            field=models.TextField(blank=True, default='', max_length=500, null=True, verbose_name='justificación'),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='archivoAdjunto',
            field=models.FileField(blank=True, help_text='El archivo adjunto de la actividad', null=True, upload_to='archivos_adjuntos/'),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='descripcion',
            field=models.TextField(max_length=500, verbose_name='descripción'),
        ),
    ]
