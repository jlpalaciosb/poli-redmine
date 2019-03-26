from django.contrib.auth.models import User,Group
from django.db import models

ESTADOS_PROYECTO = (('PENDIENTE', 'Pendiente'),
                    ('EN EJECUCION', 'En Ejecucion'),
                    ('TERMINADO', 'Terminado'),
                    ('CANCELADO', 'Cancelado'),
                    ('SUSPENDIDO', 'Suspendido'),
                    )


class Cliente(models.Model):
    """
    La clase Cliente representa a un cliente de un proyecto específico
    """
    ruc = models.CharField(verbose_name='RUC', max_length=100)
    nombre = models.CharField(verbose_name='Nombre y Apellido', max_length=50)
    direccion = models.CharField(verbose_name='Direccion', max_length=100)
    pais = models.CharField(verbose_name='Pais', max_length=20)
    correo = models.EmailField(verbose_name='Correo')
    telefono = models.CharField(verbose_name='Telefono', max_length=30)


class Proyecto(models.Model):
    """
    La clase Proyecto representa un proyecto creado por algún
    usuario
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=100,
                              help_text='El nombre del proyecto (debe ser único en el sistema)',
                              unique=True, default='MyAwesomeProject')
    descripcion = models.TextField(verbose_name='Descripcion del Proyecto', null=True, blank=True)
    cliente = models.ForeignKey(Cliente, related_name='proyecto_cliente', null=True)
    fechaInicioEstimada = models.DateField(verbose_name='Fecha de Inicio Estimada', null=True, blank=True)
    fechaFinEstimada = models.DateField(verbose_name='Fecha de Finalizacion Estimada', null=True, blank=True)
    duracionSprint = models.IntegerField(verbose_name='Duracion del Sprint', default=5)
    diasHabiles = models.IntegerField(verbose_name='Cantidad de dias Habiles en la Semana', default=5)
    estado = models.CharField(verbose_name='Estado', choices=ESTADOS_PROYECTO, max_length=30, default='PENDIENTE')
    usuario_creador = models.ForeignKey(User, related_name='usuario_contribuyente_creador')
    usuario_modificador = models.ForeignKey(User, related_name='usuario_contribuyente_modificador')



class Sprint(models.Model):
    """
    La clase Sprint representa a un Sprint de un proyecto específico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    duracion = models.IntegerField(verbose_name='Duracion')
    fechaInicio = models.DateField(verbose_name='Fecha de Inicio')
    estado = models.IntegerField(verbose_name='Estado')
    capacidad = models.IntegerField(verbose_name='Capacidad')
    miembros = models.ManyToManyField(User)
    proyecto = models.ForeignKey(Proyecto)


class Flujo(models.Model):
    """
    La clase Flujo representa a un flujo de algun proyecto especifico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto)


class Fase(models.Model):
    """
    La clase Fase representa a una fase de algun flujo específico
    """
    flujo = models.ForeignKey(Flujo)
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    orden = models.IntegerField(verbose_name='Orden')


class TipoUS(models.Model):
    """
    La clase TipoUS representa a un Tipo de User Story de un proyecto especifico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto)


class CampoPersonalizado(models.Model):
    """
    La clase CampoPersonalizado representa a un campo personalizado de un
    Tipo de User Story especifico
    """
    tipoUS = models.ForeignKey(TipoUS)
    campo = models.CharField(verbose_name='Campo Personalizado', max_length=20)
    tipoDeDato = models.CharField(verbose_name='Tipo de Dato', max_length=7)


class UserStory(models.Model):
    """
    La clase UserStory representa a un User Story de un proyecto especifico
    """
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


class ValorCampoPersonalizado(models.Model):
    """
    La clase ValorCampoPersonalizado es la representacion del valor asignado
    a un campo personalizado de un Tipo de User Story especifico
    en un User Story especifico
    """
    us = models.ForeignKey(UserStory)
    campoPersonalizado = models.ForeignKey(CampoPersonalizado)
    valor = models.CharField(verbose_name='Valor del Campo Personalizado', max_length=100)


class UserStorySprint(models.Model):
    """
    La clase UserStorySprint es la representacion de un elemento dentro del
    Sprint Backlog de un Sprint especifico
    """
    us = models.ForeignKey(UserStory)
    sprint = models.ForeignKey(Sprint)
    miembro = models.ForeignKey(User)


class Actividad(models.Model):
    """
    La clase Actividad es la representacion de una actividad de un User Story
    especifico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    descripcion = models.CharField(verbose_name='Descripcion', max_length=100)
    responsable = models.ForeignKey(User)
    # archivos adjuntos. como?
    horasTrabajadas = models.IntegerField(verbose_name='Horas Trabajadas')
    fase = models.ForeignKey(Fase)
    estado = models.IntegerField(verbose_name='Estado')
    us_sprint = models.ForeignKey(UserStorySprint)

class RolProyecto(Group):
    """

    """
    ##group = models.OneToOneField(Group, related_name='rol_es_grupo')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)

    ##class Meta:
      ##  unique_together = ("group" , "proyecto")

class RolAdministrativo(Group):
    """
        Se pretende agrupar todos los Groups que solo serviran de Rol Administrativo. Con esta clase se podra obtener ese comportamiento
    """
    ##group = models.OneToOneField(Group)


class MiembroProyecto(models.Model):
    """
    La clase
    """
    user = models.OneToOneField(User)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    roles = models.ManyToManyField(RolProyecto)
    class Meta:
        unique_together = ("user","proyecto")
    def save(self, *args, **kwargs):
        """
        Se sobreescribe el metodo para que cada vez un rol de proyecto sea anadido a un miembro, el group asociado al rol sea asociado con el usuario
        :param args:
        :param kwargs:
        :return:
        """
        if(self.id is not None):
            rolesAnteriores=MiembroProyecto.objects.get(pk=self.id).roles.all()
            for aux in rolesAnteriores:
                """
                Se le quita todos los groups de todos los roles al usuario asociado  miembro
                """
                self.user.groups.remove(aux.group_ptr)

            rolesActuales=self.roles.all()
            for aux in rolesActuales:
                self.user.groups.add(aux.group_ptr)

            self.user.save()

        super(MiembroProyecto, self).save(*args, **kwargs)
