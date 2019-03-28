from django.dispatch import receiver
from django.db.models.signals import pre_delete,post_save
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
        scrum_master.name = "Scrum Master"+instance.id
        scrum_master.proyecto = instance
        scrum_master.save()
        developer_team = RolProyecto()
        developer_team.name = "Developer Team"+instance.id
        developer_team.proyecto = instance
        developer_team.save()