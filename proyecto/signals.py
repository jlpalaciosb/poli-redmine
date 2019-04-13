from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save, pre_save, m2m_changed
from .models import MiembroProyecto, RolProyecto, Proyecto
from django.db.models.signals import pre_delete, post_save, pre_save, m2m_changed
from .models import MiembroProyecto, RolProyecto, Proyecto
from django.db.models.signals import pre_delete,post_save,pre_save,m2m_changed
from .models import MiembroProyecto,RolProyecto, Proyecto
from guardian.shortcuts import assign_perm,remove_perm
from django.contrib.auth.models import Permission
@receiver(pre_delete, sender=MiembroProyecto, dispatch_uid='miembro_delete_signal')
def quitar_group_miembro_eliminado(sender, instance, using, **kwargs):
    roles = instance.roles.all()
    for aux in roles:
        instance.user.groups.remove(aux.group_ptr)


@receiver(post_save, sender=Proyecto, dispatch_uid='roles_precargado')
def precargar_roles_proyecto(sender, instance,created,raw, using,update_fields, **kwargs):
    """
    Para cada proyecto que se crea, se agregan dos roles predeteminados: Scrum Master y Developer Team
    Como cada Rol es un Grupo. El campo name del Grupo no permite duplicados(unique) entonces el Rol si tiene un nombre que permite duplicado
    Entonces cada Rol creado tendra el nombre correspondiente pero el Grupo tendra el mismo nombre concatenado con el id del proyecto para evitar duplicados
    :param sender:
    :param instance:
    :param created:
    :param raw:
    :param using:
    :param update_fields:
    :param kwargs:
    :return:
    """
    print("HOla")
    if created:
        scrum_master = RolProyecto()
        ##scrum_master.permissions.add() anadir los permisos
        scrum_master.nombre = "Scrum Master"
        scrum_master.name = "Scrum Master"+instance.id.__str__()
        scrum_master.proyecto = instance
        scrum_master.save()
        developer_team = RolProyecto()
        developer_team.nombre = "Developer Team"
        developer_team.name = "Developer Team"+instance.id.__str__()
        developer_team.proyecto = instance
        developer_team.save()
        miembro = MiembroProyecto(user=instance.usuario_creador,proyecto=instance)
        miembro.save()
        miembro.roles.add(scrum_master)
        miembro.save()


@receiver(m2m_changed,sender=MiembroProyecto.roles.through,dispatch_uid='salvador')
def miembro_usuario(sender, instance, action, reverse, model, pk_set, using, **kwargs):
    """
    Signal que sirve para a medida que a un miembro se le modifica los roles, al usuario asociado con ese miembro tambien se le modifica los groups. Acordarse que un Rol de Proyecto es un Group
    :param sender:
    :param instance:
    :param action:
    :param reverse:
    :param model:
    :param pk_set:
    :param using:
    :param kwargs:
    :return:
    """
    print("SI")
    miembro = instance
    if action == 'post_add':
        for rol in pk_set:
            print("si")
            miembro.user.groups.add(rol)

        miembro.user.save()

    if action == 'post_remove':
        for rol in pk_set:
            print("si")
            miembro.user.groups.remove(rol)

        miembro.user.save()

@receiver(m2m_changed,sender=RolProyecto.permissions.through,dispatch_uid='rol_guardian')
def asignar_permisos_por_objeto(sender, instance, action, reverse, model, pk_set, using, **kwargs):
    """
    Signal que sirve para que cada vez que un rol de proyecto es modificado en su conjunto de permisos, se le asigne cada permiso con el proyecto en particular
    :param sender:
    :param instance: EL grupo que se anade
    :param action: Si se elimino o agrego
    :param reverse:
    :param model:
    :param pk_set: Los permisos que se agregar/quitan del rol
    :param using:
    :param kwargs:
    :return:
    """
    grupo = instance
    try:
        rol=grupo.rolproyecto
        print("Rol De Proyecto")

        proyecto=rol.proyecto
        if action == 'post_add':
            #Si se agregaron permisos entonces se le asigna
            for perm in pk_set:
                assign_perm(Permission.objects.get(pk=perm),rol,proyecto)

        if action == 'post_remove':
            #Si se quitaron permisos entonces se remueve
            for perm in pk_set:
                remove_perm(Permission.objects.get(pk=perm),rol,proyecto)

    except RolProyecto.DoesNotExist:
        #Si los permisos no pertenecn a un rol de proyecto
        pass

