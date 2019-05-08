from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin
from django.urls import reverse
from ProyectoIS2_9.utils import get_40x_or_None_ANY
from proyecto.models import Proyecto, MiembroProyecto, UserStory
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

class ModeloEstadoInvalidoMixin(object):
    """
    Mixin para prohibir acceso a una vista. Si una instancia dada del modelo model se encuentra en uno de los estados citados en estados_inaceptables
    """
    instancia_id_kwargs = 'proyecto_id'
    estados_inaceptables = []
    modelo = Proyecto
    nombre_clase = 'Proyecto'
    nombre_atributo_estado = 'estado'

    def donde_regresar(self):
        """
        Metodo que hace que se regrese a la pagina anterior si corresponde al sitio de la aplicacion o en caso contrario al menu principal

        :return:
        """
        pagina_anterior = self.request.META.get('HTTP_REFERER')
        if pagina_anterior is not None:
            return pagina_anterior
        return reverse('/')


    def dispatch(self, request, *args, **kwargs):
        if not self.sePuedeModificar(kwargs[self.instancia_id_kwargs]):
            messages.add_message(request,messages.WARNING,'El estado del {} no permite acceder a esta funcionalidad'.format(self.nombre_clase))
            return HttpResponseRedirect(self.donde_regresar())
        return super(ModeloEstadoInvalidoMixin, self).dispatch(request, *args, **kwargs)

    def sePuedeModificar(self, id):
        try:
            proyecto = self.modelo.objects.get(pk=id).__dict__
            if(proyecto[self.nombre_atributo_estado] in self.estados_inaceptables):
                return False
            return True
        except self.model.DoesNotExist:
            raise Http404('no existe {} con el id en la url'.format(self.nombre_clase))

class ProyectoEstadoInvalidoMixin(ModeloEstadoInvalidoMixin):
    """
    Mixin para prohibir acceso a una vista. Si el proyecto esta TERMINADO, CANCELADO o SUSPENDIDO.
    """
    instancia_id_kwargs = 'proyecto_id'
    estados_inaceptables = ['TERMINADO', 'CANCELADO', 'SUSPENDIDO']
    modelo = Proyecto
    nombre_clase = 'Proyecto'
    nombre_atributo_estado = 'estado'

    def donde_regresar(self):
        """
        Metodo que hace que se regrese a la pagina anterior si corresponde al sitio de la aplicacion o en caso contrario al perfil del proyecto, si el proyecto esta en un estado inaceptable.
        Sobreescribir si se quiere redirigir a otro sitio.

        :return:
        """
        pagina_anterior = self.request.META.get('HTTP_REFERER')
        if pagina_anterior is not None:
            return pagina_anterior
        return reverse('perfil_proyecto',args=(self.kwargs[self.instancia_id_kwargs],))


class ProyectoEnEjecucionMixin(ProyectoEstadoInvalidoMixin):
    """
    Mixin para prohibir acceso a una vista. Si el proyecto no esta EN EJECUCION
    """

    estados_inaceptables = ['TERMINADO', 'CANCELADO', 'SUSPENDIDO','PENDIENTE']

class Nose(object):

    clases_dependientes = [Proyecto]#, Sprint, US]
    kwargs_dependientes = ['proyecto_id', 'sprint_id', 'us_id']
    field_dependientes = ['proyecto','sprint']

    def dispatch(self, request, *args, **kwargs):
        for i in range(1,self.clases_dependientes.count()):
            busqueda = { self.field_dependientes[i] + '_id' : self.kwargs[self.kwargs_dependientes[i-1] ] }
            if self.clases_dependientes[i].objects.filter(**busqueda).count > 0 :
                return super(Nose, self).dispatch(request, *args, **kwargs)
        raise Http404('no existe proyecto con el id en la url')


class UserStoryNoModificable(object):

    def dispatch(self, request, *args, **kwargs):
        user_story =  UserStory.objects.get(pk=self.kwargs['us_id'])
        if user_story.estadoProyecto in [4, 5]:#Si el User Story esta CANCELADO o TERMINADO no se podra modificar
            messages.add_message(request, messages.WARNING, 'Ya no se puede modificar este User Story')
            return HttpResponseRedirect(reverse('proyecto_us_ver',kwargs=self.kwargs))
        return super(UserStoryNoModificable, self).dispatch(request, *args, **kwargs)