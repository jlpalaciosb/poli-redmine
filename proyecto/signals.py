from django.dispatch import receiver
from django.db.models.signals import pre_delete,post_save,pre_save,m2m_changed
from .models import MiembroProyecto,RolProyecto, Proyecto
@receiver(pre_delete, sender=MiembroProyecto, dispatch_uid='miembro_delete_signal')
def quitar_group_miembro_eliminado(sender, instance, using, **kwargs):
    roles = instance.roles.all()
    for aux in roles:
        instance.user.groups.remove(aux.group_ptr)

@receiver(post_save, sender=Proyecto, dispatch_uid='roles_precargado')
def precargar_roles_proyecto(sender, instance,created,raw, using,update_fields, **kwargs):
    print("HOla")
    if created:
        scrum_master = RolProyecto()
        ##scrum_master.permissions.add() anadir los permisos
        scrum_master.nombre = "Scrum Master"
        scrum_master.name = "Scrum Master"+instance.id.__str__()
        scrum_master.proyecto = instance
        scrum_master.save()
        developer_team = RolProyecto()
        scrum_master.nombre = "Developer Team"
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