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


class Cliente(models.Models):
    ruc = models.IntegerField(verbose_name='RUC')
    nombre = models.CharField(verbose_name='Nombre y Apellido', max_length=50)
    direccion = models.CharField(verbose_name='Direccion', max_length=100)
    pais = models.CharField(verbose_name='Pais', max_length=20)
    correo = models.EmailField(verbose_name='Correo')
    telefono = models.CharField(verbose_name='Telefono', max_length=30)


class PermisoProyecto(models.Model):
    descripcion = models.CharField(verbose_name='Descripcion', max_length=100, unique=True)


class RolDeProyecto(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=50, unique=True)
    permisos = models.ManyToManyField('PermisoProyecto')
    proyecto = models.ForeignKey(Proyecto)  # on_delete no se especifica?


class MiembroProyecto(models.Model):
    usuario = models.ForeignKey(User)
    rol = models.ManyToManyField('RolDeProyecto')


class Fase(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    orden = models.IntegerField(verbose_name='Orden')


class Flujo(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    fase = models.ForeignKey(Fase)  # oneToMany???





















































