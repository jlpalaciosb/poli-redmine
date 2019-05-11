from .models import Proyecto
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

def proyecto_en_ejecucion(function):
    """
    Prohibir acceso a una vista si el proyecto de esa vista no esta en ejecucion

    :param function:
    :return:
    """
    def wrap(request, *args, **kwargs):
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        if proyecto.estado == 'EN EJECUCION':
            return function(request, *args, **kwargs)
        else:
            messages.add_message(request,messages.WARNING,'El proyecto debe estar EN EJECUCION para acceder a esta funcionalidad')
            return HttpResponseRedirect(reverse('perfil_proyecto',args=(kwargs['proyecto_id'],)))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap