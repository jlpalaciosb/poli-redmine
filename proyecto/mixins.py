from django.core.exceptions import PermissionDenied
from django.http import Http404
from guardian.mixins import PermissionRequiredMixin

from ProyectoIS2_9.utils import get_40x_or_None_ANY
from proyecto.models import Proyecto


class GuardianAnyPermissionRequiredMixin(PermissionRequiredMixin):
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


class ProyectoMixin:
    """
    Esta clase sirve cuando en la url de la vista se define el parametro proyecto_id
    """
    def get_proyecto(self):
        try:
            p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')
        return p
