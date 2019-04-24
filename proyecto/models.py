from django.contrib.auth.models import User, Group
from django.db import models

ESTADOS_PROYECTO = (('PENDIENTE', 'Pendiente'),
                    ('EN EJECUCION', 'En Ejecucion'),
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
    descripcion = models.TextField(help_text='describa en qué consistirá el proyecto', null=True, blank=True)
    cliente = models.ForeignKey(Cliente)
    fechaInicioEstimada = models.DateField(verbose_name='inicio', help_text='fecha de inicio estimada', null=True, blank=True)
    fechaFinEstimada = models.DateField(verbose_name='finalización', help_text='fecha de finalización estimada', null=True, blank=True)
    duracionSprint = models.IntegerField(verbose_name='duración del sprint', help_text='duración estimada para los sprints (en semanas)', default=4)
    diasHabiles = models.IntegerField(verbose_name='días hábiles', help_text='cantidad de días hábiles en la semana', default=5)
    estado = models.CharField(choices=ESTADOS_PROYECTO, max_length=30, default='PENDIENTE')
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
    orden = models.IntegerField()
    duracion = models.IntegerField(verbose_name='duración del sprint (en semanas)')
    fechaInicio = models.DateField(verbose_name='fecha de inicio', null=True)
    estado = models.CharField(choices=ESTADOS_SPRINT, default='PLANIFICADO', max_length=15)
    capacidad = models.IntegerField(
        verbose_name='capacidad del sprint (en horas)', default=0,
        help_text='Este valor nos dice cuantas horas de trabajo disponible hay en el sprint'
    )

    class Meta:
        default_permissions =  ()
        unique_together = ('proyecto', 'orden')


class Flujo(models.Model):
    """
    La clase Flujo representa a un flujo de algun proyecto especifico
    """
    nombre = models.CharField(max_length=50)
    proyecto = models.ForeignKey(Proyecto)
    cantidadFases = models.IntegerField(default=0)

    class Meta:
        default_permissions = ()
        unique_together = ('proyecto', 'nombre')


class Fase(models.Model):
    """
    La clase Fase representa a una fase de algún flujo específico. Los US's están bajo una fase con un
    estado, dicho estado puede ser TO DO, DOING o DONE.
    """
    flujo = models.ForeignKey(Flujo)
    nombre = models.CharField(max_length=25)
    orden = models.IntegerField()
    
    class Meta:
        default_permissions =  ()
        unique_together = (('flujo', 'nombre'), ('flujo', 'orden'))


class TipoUS(models.Model):
    """
    La clase TipoUS representa a un Tipo de User Story de un proyecto especifico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto)

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
    ('PENDIENTE', 'Pendiente'),
    ('INICIADO', 'Iniciado'),
    ('CANCELADO', 'Cancelado'),
    ('TERMINADO', 'Terminado'),
)
PRIORIDADES_US = (
    (0, 'No Importante'),
    (1, 'Muy Baja'),
    (2, 'Baja'),
    (3, 'Media'),
    (4, 'Alta'),
    (5, 'Muy Alta'),
    (6, 'Super Importante'),
)
class UserStory(models.Model):
    """
    La clase UserStory representa a un User Story de un proyecto específico
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(verbose_name='descripción', max_length=500)
    criterioAceptacion = models.TextField(
        verbose_name='criterios de aceptación',
        help_text='condiciones para que el US sea aceptado como terminado'
    )

    tipo = models.ForeignKey(TipoUS)

    proyecto = models.ForeignKey(Proyecto)
    estadoProyecto = models.CharField(
        verbose_name='estado del US en el proyecto', max_length=15,
        choices=ESTADOS_US_PROYECTO, default='PENDIENTE',
    )

    flujo = models.ForeignKey(Flujo, verbose_name='flujo que debe seguir el US', null=True)
    fase = models.ForeignKey(Fase, verbose_name='fase en la que se encuentra el US', null=True)
    estadoFase = models.CharField(
        verbose_name='estado en la fase', max_length=10,
        choices=ESTADOS_US_FASE, null=True,
    )

    prioridad = models.IntegerField(choices=PRIORIDADES_US, default=3)
    valorNegocio = models.IntegerField(verbose_name='valor de negocio', default=1)
    valorTecnico = models.IntegerField(verbose_name='valor técnico', default=1)

    tiempoPlanificado = models.IntegerField(
        verbose_name='tiempo planificado (en horas)',
        help_text='cuántas horas cree que le llevará a una persona terminar este US',
    )
    tiempoEjecutado = models.FloatField(verbose_name='tiempo ejecutado (en horas)', default=0)

    class Meta:
        default_permissions =  ()


class ValorCampoPersonalizado(models.Model):
    """
    La clase ValorCampoPersonalizado es la representacion del valor asignado
    a un campo personalizado de un Tipo de User Story especifico
    en un User Story especifico
    """
    us = models.ForeignKey(UserStory)
    campoPersonalizado = models.ForeignKey(CampoPersonalizado)
    valor = models.CharField(verbose_name='Valor del Campo Personalizado', max_length=100)

    class Meta:
        default_permissions =  ()
        unique_together = ("us", "campoPersonalizado")


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
    """
    miembro = models.ForeignKey(MiembroProyecto, verbose_name='Miembro del Sprint')
    sprint = models.ForeignKey(Sprint, verbose_name='Sprint')
    horasAsignadas = models.IntegerField(verbose_name='Horas por día asignadas al miembro')

    class Meta:
        unique_together = ('miembro', 'sprint')


class UserStorySprint(models.Model):
    """
    La clase UserStorySprint sirve para asignar un US al Sprint Backlog de un sprint
    """
    us = models.ForeignKey(UserStory)
    sprint = models.ForeignKey(Sprint)
    asignee = models.ForeignKey(MiembroSprint)

    class Meta:
        default_permissions = ()
        unique_together = ('us', 'sprint')


class Actividad(models.Model):
    """
    La clase Actividad es la representación de una actividad de un User Story específico
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(verbose_name='descripción', max_length=500)
    usSprint = models.ForeignKey(UserStorySprint)

    # no sirve obtener quien fue el responsable de la actividad por medio de usSprint ya que un US
    # del Sprint Backlog se podría asignar a otro miembro durante el sprint, por eso es que se agrega
    # este atributo
    responsable = models.ForeignKey(MiembroSprint)

    # por ahora todavía no tenemos una clase para archivos adjuntos, en dicha clase se deberá
    # especificar el ForeignKey a Actividad

    horasTrabajadas = models.IntegerField(verbose_name='horas trabajadas', default=0)
    fase = models.ForeignKey(Fase)

    # especifica en que estado estaba el US cuando la actividad fue agregada
    estado = models.CharField(choices=ESTADOS_US_FASE, default='DOING', max_length=10)

    class Meta:
        default_permissions = ()
