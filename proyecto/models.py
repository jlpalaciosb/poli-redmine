from django.contrib.auth.models import User
from django.db import models

ESTADOS_PROYECTO=(('PENDIENTE', 'Pendiente'),
                   ('EN EJECUCION', 'En Ejecucion'),
                   ('TERMINADO', 'Terminado'),
                   ('CANCELADO', 'Cancelado'),
                   ('SUSPENDIDO', 'Suspendido'),
                   )


class Proyecto(models.Model):
    """
    La clase Proyecto representa un proyecto creado por algún
    usuario
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=100,
                              help_text='El nombre del proyecto (debe ser único en el sistema)',
                              unique=True, default='MyAwesomeProject')
    descripcion = models.TextField(verbose_name='Descripcion del Proyecto', null=True, blank=True)
    # cliente= models.ForeignKey(Cliente,related_name='proyecto_cliente')
    fechaInicioEstimada = models.DateField(verbose_name='Fecha de Inicio Estimada', null=True, blank=True)
    fechaFinEstimada = models.DateField(verbose_name='Fecha de Finalizacion Estimada', null=True, blank=True)
    duracionSprint = models.IntegerField(verbose_name='Duracion del Sprint',default=5)
    diasHabiles = models.IntegerField(verbose_name='Cantidad de dias Habiles en la Semana',default=5)
    estado = models.CharField(verbose_name='Estado', choices=ESTADOS_PROYECTO,max_length=30,default='PENDIENTE')
    usuario_creador = models.ForeignKey(User, related_name='usuario_contribuyente_creador')
    usuario_modificador = models.ForeignKey(User, related_name='usuario_contribuyente_modificador')


class PermisoProyecto(models.Model):
    descripcion = models.CharField(verbose_name='Descripcion', max_length=100, unique=True)


class RolDeProyecto(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=50, unique=True)
    proyecto = models.ForeignKey(Proyecto)  # on_delete no se especifica?
    permisos = models.ManyToManyField('PermisoProyecto')
