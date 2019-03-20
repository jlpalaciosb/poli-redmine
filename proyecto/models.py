from django.contrib.auth.models import User
from django.db import models

ESTADOS_PROYECTO = (('PENDIENTE', 'Pendiente'),
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
    duracionSprint = models.IntegerField(verbose_name='Duracion del Sprint', default=5)
    diasHabiles = models.IntegerField(verbose_name='Cantidad de dias Habiles en la Semana', default=5)
    estado = models.CharField(verbose_name='Estado', choices=ESTADOS_PROYECTO, max_length=30, default='PENDIENTE')
    usuario_creador = models.ForeignKey(User, related_name='usuario_contribuyente_creador')
    usuario_modificador = models.ForeignKey(User, related_name='usuario_contribuyente_modificador')


class Cliente(models.Model):
    ruc = models.IntegerField(verbose_name='RUC')
    nombre = models.CharField(verbose_name='Nombre y Apellido', max_length=50)
    direccion = models.CharField(verbose_name='Direccion', max_length=100)
    pais = models.CharField(verbose_name='Pais', max_length=20)
    correo = models.EmailField(verbose_name='Correo')
    telefono = models.CharField(verbose_name='Telefono', max_length=30)


"""
class PermisoProyecto(models.Model):
    descripcion = models.CharField(verbose_name='Descripcion', max_length=100, unique=True)


class RolDeProyecto(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=50, unique=True)
    permisos = models.ManyToManyField('PermisoProyecto')
    proyecto = models.ForeignKey(Proyecto)  # on_delete no se especifica?


class MiembroProyecto(models.Model):
    usuario = models.ForeignKey(User)
    rol = models.ManyToManyField('RolDeProyecto')
"""


class Sprint(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    duracion = models.IntegerField(verbose_name='Duracion')
    fechaInicio = models.DateField(verbose_name='Fecha de Inicio')
    estado = models.IntegerField(verbose_name='Estado')
    capacidad = models.IntegerField(verbose_name='Capacidad')
    miembros = models.ManyToManyField(User)


class Flujo(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=20)


class Fase(models.Model):
    flujo = models.ForeignKey(Flujo)
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    orden = models.IntegerField(verbose_name='Orden')


class TipoUS(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=20)


class CampoPersonalizado(models.Model):
    tipoUS = models.ForeignKey(TipoUS)
    campo = models.CharField(verbose_name='Campo Personalizado', max_length=20)
    tipoDeDato = models.CharField(verbose_name='Tipo de Dato', max_length=7)


class UserStory(models.Model):
    descripcionCorta = models.CharField(verbose_name='Descripcion Corta', max_length=50)
    descripcion = models.CharField(verbose_name='Descripcion', max_length=100)
    criterioAceptacion = models.CharField(verbose_name='Criterio de Aceptacion', max_length=100)
    valorNegocio = models.IntegerField(verbose_name='Valor de Negocio')
    valorTecnico = models.IntegerField(verbose_name='Valor Tecnico')
    prioridad = models.IntegerField(verbose_name='Prioridad')
    tiempoPlanificado = models.IntegerField(verbose_name='Tiempo Planificado')
    tiempoEjecutado = models.IntegerField(verbose_name='Tiempo Ejecutado')
    estadoSistema = models.IntegerField(verbose_name="Estado en el Sistema")
    tipo = models.ForeignKey(TipoUS)
    flujo = models.ForeignKey(Flujo)
    faseActual = models.IntegerField(verbose_name='Fase actual en el flujo')
    estadoFaseActual = models.IntegerField(verbose_name='Estado actual en la fase actual del flujo')
    proyecto = models.ForeignKey(Proyecto)
    sprint = models.ForeignKey(Sprint)


class ValorCampoPersonalizado(models.Model):
    us = models.ForeignKey(UserStory)
    tipoUs = models.ForeignKey(TipoUS)
    valor = models.CharField(verbose_name='Valor del Campo Personalizado', max_length=100)


class UserStorySprint(models.Model):
    us = models.ForeignKey(UserStory)
    sprint = models.ForeignKey(Sprint)
    miembro = models.ForeignKey(User)


class Actividad(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    descripcion = models.CharField(verbose_name='Descripcion', max_length=100)
    # archivos adjuntos. como?
    horasTrabajadas = models.IntegerField(verbose_name='Horas Trabajadas')
    fase = models.ForeignKey(Fase)  # sin relacion directa con el flujo?
    estado = models.IntegerField(verbose_name='Estado')
    us_sprint = models.Model(UserStorySprint)
