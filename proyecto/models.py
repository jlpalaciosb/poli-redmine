from django.contrib.auth.models import User, Group
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
import datetime
from django.core.validators import MinValueValidator
def validar_mayor_a_cero(value):
    if value == 0:
        raise ValidationError(
            'No se permite el cero. Debe ser un numero mayor'
        )

ESTADOS_PROYECTO = (('PENDIENTE', 'Pendiente'),
                    ('EN EJECUCION', 'En Ejecución'),
                    ('TERMINADO', 'Terminado'),
                    ('CANCELADO', 'Cancelado'),
                    ('SUSPENDIDO', 'Suspendido'),
                    )

VALOR_CAMPO = (('NUMERO', 'Numero'),
               ('STRING', 'String'),
               )


class Cliente(models.Model):
    """
    La clase Cliente representa a un cliente de uno o varios proyectos
    """
    ruc = models.CharField(verbose_name='RUC', max_length=15, unique=True)
    nombre = models.CharField(max_length=60)
    direccion = models.CharField(verbose_name='dirección', max_length=100)
    pais = models.CharField(verbose_name='país', max_length=50)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(verbose_name='teléfono', max_length=30, unique=True)

    def __str__(self):
        return "(RUC: {}) {}".format(self.ruc, self.nombre)

    class Meta:
        default_permissions =  ()
        permissions = ( ('add_cliente', 'Agregar Cliente'), ('change_cliente', 'Modificar Cliente'), ('delete_cliente', 'Eliminar Cliente') )


class Proyecto(models.Model):
    """
    La clase Proyecto representa un proyecto
    """
    nombre = models.CharField(max_length=100, unique=True, default='My Awesome Project')
    descripcion = models.TextField(verbose_name='descripción', help_text='describa en qué consistirá el proyecto', null=True, blank=True)
    cliente = models.ForeignKey(Cliente)
    fechaInicioEstimada = models.DateField(verbose_name='inicio', help_text='fecha de inicio estimada', null=True, blank=True)
    fechaFinEstimada = models.DateField(verbose_name='finalización', help_text='fecha de finalización estimada', null=True, blank=True)
    duracionSprint = models.PositiveIntegerField(verbose_name='duración del sprint', help_text='duración estimada para los sprints (en semanas)', default=4, validators=[validar_mayor_a_cero])
    diasHabiles = models.PositiveIntegerField(verbose_name='días hábiles', help_text='cantidad de días hábiles en la semana', default=5, validators=[validar_mayor_a_cero])
    estado = models.CharField(choices=ESTADOS_PROYECTO, max_length=30, default='PENDIENTE')
    justificacion = models.TextField(verbose_name='justificación', null=True, blank=True, default="", max_length=500)
    scrum_master = models.ForeignKey(User, verbose_name='scrum master')

    class Meta:
        default_permissions = ()
        permissions = (
            ('add_proyecto', 'Agregar Proyecto'),
            ('change_proyecto', 'Modificar Proyecto'),
            ('delete_proyecto', 'Eliminar Proyecto'),
            ('add_rolproyecto', 'Agregar Rol al Proyecto'),
            ('change_rolproyecto', 'Modificar Rol del Proyecto'),
            ('delete_rolproyecto', 'Eliminar Rol del Proyecto'),
            ('add_miembroproyecto', 'Agregar Miembro al Proyecto'),
            ('change_miembroproyecto', 'Modificar Miembro del Proyecto'),
            ('delete_miembroproyecto', 'Eliminar Miembro del Proyecto'),
            ('add_tipous', 'Agregar Tipo User Story al Proyecto'),
            ('change_tipous', 'Modificar Tipo User Story del Proyecto'),
            ('delete_tipous', 'Eliminar Tipo US del Proyecto'),
            ('add_flujo', 'Agregar Flujo al Proyecto'),
            ('change_flujo', 'Modificar Flujo del Proyecto'),
            ('delete_flujo', 'Eliminar Flujo del Proyecto'),
            ('add_us', 'Agregar User Story al Proyecto'),
            ('change_us', 'Modificar User Story del Proyecto'),
            ('delete_us', 'Eliminar User Story del Proyecto'),
            ('administrar_sprint', 'Administrar Sprints del Proyecto'),
            ('desarrollador_proyecto', 'Realizar US')
        )


ESTADOS_SPRINT = (
    ('PLANIFICADO', 'Planificado'),
    ('EN_EJECUCION', 'En Ejecución'),
    ('CERRADO', 'Cerrado'),
)
class Sprint(models.Model):
    """
    La clase Sprint representa a un Sprint de un proyecto específico
    """
    proyecto = models.ForeignKey(Proyecto)
    orden = models.PositiveIntegerField(validators=[validar_mayor_a_cero])
    duracion = models.PositiveIntegerField(verbose_name='duración del sprint (en semanas)', validators=[validar_mayor_a_cero])
    fechaInicio = models.DateField(verbose_name='fecha de inicio', null=True)
    estado = models.CharField(choices=ESTADOS_SPRINT, default='PLANIFICADO', max_length=15)
    justificacion= models.CharField(verbose_name='Justificacion', null=True,blank=True,default="",max_length=300)
    capacidad = models.PositiveIntegerField(
        verbose_name='capacidad del sprint (en horas)', default=0,
        help_text='Este valor nos dice cuántas horas de trabajo disponible hay en el sprint'
    )
    fecha_fin = models.DateField(verbose_name='fecha de finalizacion', null=True, help_text='La fecha en la que finaliza un sprint')

    class Meta:
        default_permissions =  ()
        unique_together = ('proyecto', 'orden')

    def flujos_sprint(self):
        """
        Devuelve todos los flujos que corresponden a un sprint
        :return:
        """
        flujos = list(map(lambda us_sprint: us_sprint.us.flujo.id,list(self.userstorysprint_set.all())))
        return Flujo.objects.filter(id__in=flujos)


    def save(self, *args, **kwargs):
        """
        Al cerrar un sprint todos los user stories que no hayan terminado se les coloca en el estado NO TERMINADO
        :param args:
        :param kwargs:
        :return:
        """
        super(Sprint, self).save( *args, **kwargs)
        self.user_stories_sprint_cerrado()


    def user_stories_sprint_cerrado(self):
        """
        Todos los user stories que su estado no sea TERMINADO se les cambia el estado a NO TERMINADO
        :return:
        """
        if self.estado == 'CERRADO':#Si un sprint se cerro
            for user_story_sprint in self.userstorysprint_set.all():
                if user_story_sprint.us.estadoProyecto != 5:#Entonces todos los user stories que no este terminados se les coloca el estado no terminado
                    user_story_sprint.us.estadoProyecto = 3 # Se coloca en el estado de No Terminado
                    user_story_sprint.us.save()

    def tiempo_restante(self):
        """
        Metodo para calcular el tiempo restante del sprint si es que esta en ejecucion. Se tiene en cuenta todos los dias de la semana
        :return: La cantidad en dias del tiempo restante o None si no es posible hallar
        """
        if self.estado == 'EN_EJECUCION' and self.fechaInicio is not None:
            return self.duracion * 7 - (datetime.date.today() - self.fechaInicio).days
        return None


class Flujo(models.Model):
    """
    La clase Flujo representa a un flujo de algun proyecto especifico
    """
    nombre = models.CharField(max_length=50)
    proyecto = models.ForeignKey(Proyecto)
    cantidadFases = models.PositiveIntegerField(default=0)

    class Meta:
        default_permissions = ()
        unique_together = ('proyecto', 'nombre')

    def __str__(self): return self.nombre


class Fase(models.Model):
    """
    La clase Fase representa a una fase de algún flujo específico. Los US's están bajo una fase con un
    estado, dicho estado puede ser TO DO, DOING o DONE.
    """
    flujo = models.ForeignKey(Flujo)
    nombre = models.CharField(max_length=25)
    orden = models.PositiveIntegerField(default=1, help_text='El orden de la fase dentro de su flujo correspondiente. Comienza desde cero')

    class Meta:
        default_permissions = ()
        unique_together = (('flujo', 'nombre'), ('flujo', 'orden'))
        ordering = ['orden']

    def es_ultima_fase(self):
        return self.orden == self.flujo.cantidadFases


class TipoUS(models.Model):
    """
    La clase TipoUS representa a un Tipo de User Story de un proyecto especifico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto)

    def __str__(self):
        return self.nombre

    class Meta:
        default_permissions =  ()
        unique_together = ('nombre', 'proyecto')


class CampoPersonalizado(models.Model):
    """
    La clase CampoPersonalizado representa a un campo personalizado de un
    Tipo de User Story especifico
    """
    tipoUS = models.ForeignKey(TipoUS)
    tipo_dato = models.CharField(verbose_name='Tipo de dato del Campo', choices=VALOR_CAMPO, max_length=7, default='STRING')
    nombre_campo = models.CharField(verbose_name='Nombre del campo', max_length=20)

    class Meta:
        default_permissions =  ()
        unique_together = ("tipoUS", "nombre_campo")


ESTADOS_US_FASE = (('TODO', 'To Do'), ('DOING', 'Doing'), ('DONE', 'Done'))
ESTADOS_US_PROYECTO = (
    (1, 'Pendiente'),
    (2, 'En Sprint'),
    (3, 'No Terminado'), # estado cuando el us fue parte del sprint anterior pero no se termino
    (4, 'Cancelado'),
    (5, 'Terminado'),
    (6, 'En Revision')
)
PRIORIDADES_US = (
    (1, 'Muy Bajo'),
    (2, 'Bajo'),
    (3, 'Normal'),
    (4, 'Alto'),
    (5, 'Muy Alto'),
)
def default_vals(): return {'c1': 'v1', 'c2': 2}
class UserStory(models.Model):
    """
    La clase UserStory representa a un User Story de un proyecto específico
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(verbose_name='descripción')
    criteriosAceptacion = models.TextField(
        verbose_name='criterios de aceptación',
        help_text='condiciones para que el US sea aceptado como terminado'
    )

    tipo = models.ForeignKey(TipoUS)
    valoresCPs = JSONField(default=default_vals) # Será un diccionario donde la clave de los items es el nombre del campo pers. y el valor es el valor del campo pers.

    proyecto = models.ForeignKey(Proyecto)
    estadoProyecto = models.IntegerField(
        verbose_name='estado del US en el proyecto', choices=ESTADOS_US_PROYECTO, default=1,
    )

    flujo = models.ForeignKey(Flujo, verbose_name='flujo que debe seguir el US', null=True)
    fase = models.ForeignKey(Fase, verbose_name='fase en la que se encuentra el US', null=True)
    estadoFase = models.CharField(
        verbose_name='estado en la fase', max_length=10,
        choices=ESTADOS_US_FASE, null=True,
    )

    prioridad = models.PositiveIntegerField(choices=PRIORIDADES_US, default=3)
    valorNegocio = models.PositiveIntegerField(verbose_name='valor de negocio', choices=PRIORIDADES_US, default=3)
    valorTecnico = models.PositiveIntegerField(verbose_name='valor técnico', choices=PRIORIDADES_US, default=3)
    priorizacion = models.FloatField(default=1)

    tiempoPlanificado = models.PositiveIntegerField(
        verbose_name='tiempo planificado (en horas)',
        help_text='cuántas horas cree que le llevará a una persona terminar este US',
    )
    tiempoEjecutado = models.PositiveIntegerField(verbose_name='tiempo ejecutado (en horas)', default=0)

    justificacion = models.CharField(verbose_name='Justificacion', null=True, blank=True, default="", max_length=300)

    class Meta:
        default_permissions =  ()
        unique_together = ('proyecto', 'nombre')

    def __str__(self):
        return self.nombre

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.priorizacion = (4 * self.prioridad + self.valorTecnico + self.valorNegocio) / 6
        self.pasar_a_revision()
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def pasar_a_revision(self):
        # Si llego al DONE de su ultima fase entonces su estado general pasa a ser EN REVISION
        if self.fase is not None and self.fase.orden == self.flujo.cantidadFases and self.estadoFase == 'DONE':
            self.estadoProyecto = 6

    def tiene_tiempo_excedido(self):
        """
        Metodo en el que se comprueba si el tiempo ejecutado excedio si el US no termino en un sprint
        :return:
        """
        if self.estadoProyecto == 3:
            return not self.tiempoPlanificado>self.tiempoEjecutado
        return False



class RolProyecto(Group):
    """
    """
    # group = models.OneToOneField(Group, related_name='rol_es_grupo')
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)#indica si el atributo es por defecto
    class Meta:
        default_permissions = ()
        unique_together = ("nombre", "proyecto")


class RolAdministrativo(Group):
    """
    Se pretende agrupar todos los Groups que solo serviran de Rol Administrativo.
    Con esta clase se podra obtener ese comportamiento
    """
    # group = models.OneToOneField(Group)

    class Meta:
        default_permissions =  ()
        permissions = ( ('add_roladministrativo', 'Agregar Rol Administrativo'), ('change_roladministrativo', 'Modificar Rol Administrativo'), ('delete_roladministrativo', 'Eliminar Rol Administrativo') )


class MiembroProyecto(models.Model):
    """
    La clase representa a un miembro de un proyecto con sus roles del Proyecto
    """
    user = models.ForeignKey(User, verbose_name='Usuario')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    roles = models.ManyToManyField(RolProyecto)

    class Meta:
        default_permissions = ()
        unique_together = (("user","proyecto"),)

    def __str__(self):
        return self.user.__str__()


class Usuario(models.Model):

    class Meta:
        default_permissions = ()
        permissions = (('add_usuario', 'Agregar Usuario'),
                       ('change_usuario', 'Modificar Usuario'),
                       ('delete_usuario', 'Eliminar Usuario'))


class MiembroSprint(models.Model):
    """
    Representa la relacion entre un Sprint y un Miembro, cuando es asignado como desarrollador.
    Almacena la cantidad de horas de trabajo asignadas a ese miembro para ese Sprint especifico.
    Cada vez que se agregue una instancia de esta clase, la capacidad del sprint con quien este asociado dicha instancia sera actualizada
    """
    miembro = models.ForeignKey(MiembroProyecto, verbose_name='Miembro del Sprint')
    sprint = models.ForeignKey(Sprint, verbose_name='Sprint')
    horasAsignadas = models.PositiveIntegerField(verbose_name='Horas por día asignadas al miembro', validators=[validar_mayor_a_cero])

    class Meta:
        unique_together = ('miembro', 'sprint')

    def __str__(self):
        return self.miembro.user.username


class UserStorySprint(models.Model):
    """
    La clase UserStorySprint sirve para asignar un US al Sprint Backlog de un sprint
    """
    us = models.ForeignKey(UserStory, verbose_name='User Story')
    sprint = models.ForeignKey(Sprint)
    asignee = models.ForeignKey(MiembroSprint, null=True, verbose_name='Encargado')

    fase_sprint = models.ForeignKey(Fase, verbose_name='fase en la que se encuentra el US', null=True, help_text='Fase en la que se encuentra un user story en un sprint')

    estado_fase_sprint = models.CharField(
        verbose_name='estado en la fase', max_length=10,
        choices=ESTADOS_US_FASE, null=True, help_text='Estado en el que se encuentra un user story en un sprint'
    )

    class Meta:
        default_permissions = ()
        unique_together = ('us', 'sprint')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Se actualiza el metodo para que al guardar/actualizar un user story en un sprint, si el sprint esta planificado o en ejecucion se sincronize los campos del user story
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        super(UserStorySprint, self).save(force_insert, force_update, using, update_fields)
        self.sincronizar_user_story_asociado()


    def sincronizar_user_story_asociado(self):
        """
        Se actualiza los campos de fase y estado del User Story asociado de acuerdo al moviemiento del US asociado siempre y cuando el sprint este planificado o en ejecucion
        :return:
        """
        if self.sprint.estado == 'EN_EJECUCION' or self.sprint.estado == 'PLANIFICADO' :
            self.us.fase = self.fase_sprint
            self.us.estadoFase = self.estado_fase_sprint
            self.us.save()


class Actividad(models.Model):
    """
    La clase Actividad es la representación de una actividad de un User Story específico
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(verbose_name='descripción', max_length=500)
    usSprint = models.ForeignKey(UserStorySprint)

    # no sirve obtener quien fue el responsable de la actividad por medio de usSprint ya que un US
    # del Sprint Backlog se podría asignar a otro miembro durante el sprint, por eso es que se agrega
    # este atributo
    responsable = models.ForeignKey(MiembroProyecto)

    horasTrabajadas = models.PositiveIntegerField(verbose_name='horas trabajadas', default=0)
    fase = models.ForeignKey(Fase)

    archivoAdjunto = models.FileField(upload_to='archivos_adjuntos/', help_text='El archivo adjunto de la actividad', null=True, blank=True)

    # especifica en que estado estaba el US cuando la actividad fue agregada
    estado = models.CharField(choices=ESTADOS_US_FASE, default='DOING', max_length=10)

    # especifica la fecha y hora en la que se agregó la actividad
    fechaHora = models.DateTimeField(verbose_name='fecha y hora de registro', auto_now=True, null=False)

    class Meta:
        default_permissions = ()

    def save(self, *args, **kwargs):
        if self.id is None:
            anterior = 0
        else:
            anterior = Actividad.objects.get(pk=self.id).horasTrabajadas

        super(Actividad, self).save(*args, **kwargs)

        self.acumular_horas_user_story(anterior)

    def acumular_horas_user_story(self, anterior):
        """
        Metodo que sumas las horas trabajadas en la actividad al user story correspondiente
        :param anterior: Las horas trabajadas del registro anterior
        :return:
        """
        if self.usSprint is not None and self.usSprint.us is not None:
            us = self.usSprint.us
            if us.tiempoEjecutado >= 0 and self.horasTrabajadas>=0:
                us.tiempoEjecutado = us.tiempoEjecutado - anterior# EN CASO DE QUE SE MODIFIQUE. SE DESCARTA LAS HORAS ANTERIORES
                us.tiempoEjecutado = us.tiempoEjecutado + self.horasTrabajadas
                us.save()
