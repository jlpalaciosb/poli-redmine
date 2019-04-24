from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden
from django.contrib.auth.mixins import PermissionRequiredMixin
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from ProyectoIS2_9.utils import get_40x_or_None_ANY
from proyecto.models import Proyecto, MiembroProyecto
from django.contrib import messages
from django.views.generic import DeleteView

class PermisosPorProyectoMixin(GuardianPermissionRequiredMixin):
    """
    Clase a ser heredada por las vistas que necesitan autorizacion de permisos para un proyecto en particular. Se debe especificar la lista de permisos
    """
    return_403 = True
    proyecto_param = 'proyecto_id'#El parametro que contiene el id del proyecto a verificar

    def get_permission_object(self):
        """
        Metodo que obtiene el proyecto con el cual los permisos a verificar deberian estar asociados
        :return:
        """
        try:
            p = Proyecto.objects.get(pk=self.kwargs[self.proyecto_param])
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')
        return p


class PermisosEsMiembroMixin(PermissionRequiredMixin):
    """
    Clase a ser heredada por las vistas de un proyecto que necesitan comprobar si un usuario es miembro de un proyecto para permitir acceso a las mismas.
    Es decir, si es miembro del proyecto podra acceder a la vista. Usada gralmente para vistas que involucran solo visualizacion
    """
    proyecto_param = 'proyecto_id'  # El parametro que contiene el id del proyecto a verificar

    def has_permission(self):
        """
        Si el usuario que hace el request es miembro del proyecto por quien solicita entonces tiene permisos
        :return: True si el usuario es miembro y false si el usuario no es miembro del proyecto
        """
        try:
            MiembroProyecto.objects.get(user=self.request.user, proyecto__pk=self.kwargs[self.proyecto_param])
            return True
        except MiembroProyecto.DoesNotExist:
            return False

    def handle_no_permission(self):
        return HttpResponseForbidden()


class GuardianAnyPermissionRequiredMixin(GuardianPermissionRequiredMixin):
    def check_permissions(self, request):
        """
        Checks if *request.user* has ANY of the permissions returned by
        *get_required_permissions* method.

        :param request: Original request.
        """
        obj = self.get_permission_object()

        forbidden = get_40x_or_None_ANY(request,
                                    perms=self.get_required_permissions(
                                        request),
                                    obj=obj,
                                    login_url=self.login_url,
                                    redirect_field_name=self.redirect_field_name,
                                    return_403=self.return_403,
                                    return_404=self.return_404,
                                    accept_global_perms=self.accept_global_perms
                                    )
        if forbidden:
            self.on_permission_check_fail(request, forbidden, obj=obj)
        if forbidden and self.raise_exception:
            raise PermissionDenied()
        return forbidden

class SuccessMessageOnDeleteMixin():

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteView, self).delete(request, *args, **kwargs)