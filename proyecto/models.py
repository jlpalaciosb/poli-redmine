from django.db import models

class Proyecto(models.Model):
    """
    La clase Proyecto representa un proyecto creado por algún
    usuario
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=100,
                              help_text='El nombre del proyecto (debe ser único en el sistema)')
