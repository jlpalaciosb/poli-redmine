from django.dispatch import receiver
from django.db.models.signals import pre_delete
from .models import MiembroProyecto
@receiver(pre_delete, sender=MiembroProyecto, dispatch_uid='miembro_delete_signal')
def quitar_group_miembro_eliminado(sender, instance, using, **kwargs):
    roles = instance.roles.all()
    for aux in roles:
        instance.user.groups.remove(aux.group_ptr)
