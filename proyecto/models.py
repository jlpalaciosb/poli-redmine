from django.db import models

class Proyecto(models.Model):
    nombre=models.CharField(verbose_name='Nombre',max_length=100)

