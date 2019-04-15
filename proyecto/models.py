from django.contrib.auth.models import User,Group
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
    La clase Proyecto representa un proyecto creado por algún
    usuario
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=100,
                              help_text='El nombre del proyecto (debe ser único en el sistema)',
                              unique=True, default='MyAwesomeProject')
    descripcion = models.TextField(verbose_name='Descripcion del Proyecto', null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=True)
    fechaInicioEstimada = models.DateField(verbose_name='Fecha de Inicio Estimada', null=True, blank=True)
    fechaFinEstimada = models.DateField(verbose_name='Fecha de Finalizacion Estimada', null=True, blank=True)
    duracionSprint = models.IntegerField(verbose_name='Duracion del Sprint',help_text='La duracion del sprint debe estar en semanas', default=5)
    diasHabiles = models.IntegerField(verbose_name='Cantidad de dias Habiles en la Semana', default=5)
    estado = models.CharField(verbose_name='Estado', choices=ESTADOS_PROYECTO, max_length=30, default='PENDIENTE')
    scrum_master = models.ForeignKey(User, verbose_name='Scrum Master', related_name='scrum_master_proyecto_creador')

    class Meta:
        default_permissions = ()
        permissions = ( ('add_proyecto', 'Agregar Proyecto'),
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


    class Meta:
        default_permissions =  ()


class Flujo(models.Model):
    """
    La clase Flujo representa a un flujo de algun proyecto especifico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto)

    class Meta:
        default_permissions =  ()


class Fase(models.Model):
    """
    La clase Fase representa a una fase de algún flujo específico. Los US's están bajo una fase con un
    estado, dicho estado puede ser TO DO, DOING o DONE.
    """
    flujo = models.ForeignKey(Flujo)
    nombre = models.CharField(max_length=20)

    class Meta:
        default_permissions =  ()
        unique_together = ('flujo', 'nombre')


class TipoUS(models.Model):
    """
    La clase TipoUS representa a un Tipo de User Story de un proyecto especifico
    """
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto)

    class Meta:
        default_permissions =  ()


class CampoPersonalizado(models.Model):
    """
    La clase CampoPersonalizado representa a un campo personalizado de un
    Tipo de User Story especifico
    """
    tipoUS = models.ForeignKey(TipoUS)
    estado = models.CharField(verbose_name='Estado', choices=ESTADOS_PROYECTO, max_length=30, default='PENDIENTE')
    campo = models.CharField(verbose_name='Campo Personalizado', choices=VALOR_CAMPO, max_length=20, default='STRING')
    tipoDeDato = models.CharField(verbose_name='Tipo de Dato', max_length=7)

    class Meta:
        default_permissions =  ()
        unique_together = ("tipoUS", "campo")


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
    tipo = models.ForeignKey(TipoUS)
    criterioAceptacion = models.CharField(
        verbose_name='criterio de aceptación',
        max_length=500,
        help_text='Aquí podría especificar las características del producto resultado de las actividades '
                  'de un US, para que el US sea aceptado'
    )

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
        help_text='Especifique cuántas horas cree que le llevará a una persona terminar este US',
    )
    tiempoEjecutado = models.IntegerField(verbose_name='tiempo ejecutado (en horas)')

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



class UserStorySprint(models.Model):
    """
    La clase UserStorySprint es la representacion de un elemento dentro del
    Sprint Backlog de un Sprint especifico
    """
    us = models.ForeignKey(UserStory)
    sprint = models.ForeignKey(Sprint)
    miembro = models.ForeignKey(User)

    class Meta:
        default_permissions =  ()


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

    class Meta:
        default_permissions =  ()

class RolProyecto(Group):
    """

    """
    ##group = models.OneToOneField(Group, related_name='rol_es_grupo')
    nombre = models.CharField(verbose_name='Nombre', max_length=20)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)

    class Meta:
        default_permissions = ()
        unique_together = ("nombre" , "proyecto")

class RolAdministrativo(Group):
    """
        Se pretende agrupar todos los Groups que solo serviran de Rol Administrativo. Con esta clase se podra obtener ese comportamiento
    """
    ##group = models.OneToOneField(Group)

    class Meta:
        default_permissions =  ()
        permissions = ( ('add_roladministrativo', 'Agregar Rol Administrativo'), ('change_roladministrativo', 'Modificar Rol Administrativo'), ('delete_roladministrativo', 'Eliminar Rol Administrativo') )


class MiembroProyecto(models.Model):
    """
    La clase
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