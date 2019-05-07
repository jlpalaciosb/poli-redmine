from __future__ import unicode_literals

import logging
import os

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render
from guardian.conf import settings as guardian_settings

from proyecto.models import UserStorySprint

logger = logging.getLogger(__name__)
abspath = lambda *p: os.path.abspath(os.path.join(*p))


# retorna true si el usuario tiene uno de los permisos
def cualquier_permiso(user, perms):
    for perm in perms:
        if user.has_perm(perm):
            return True
    return False


# retorna true si el usuario es administrador
def es_administrador(user):
    return user.groups.filter(name='Administrador').count() == 1


def get_40x_or_None_ANY(request, perms, obj=None, login_url=None,
                    redirect_field_name=None, return_403=False,
                    return_404=False, accept_global_perms=False):
    """
    Este es un copy paste de guardian.utils.get_40x_or_None que lo que hace es verificar
    que el usuario tenga al menos un permiso de los permisos definidos en perm. Basicamente lo
    unico que se hizo fue reemplazar el built-in de python all por any
    :param request:
    :param perms:
    :param obj:
    :param login_url:
    :param redirect_field_name:
    :param return_403:
    :param return_404:
    :param accept_global_perms:
    :return:
    """
    login_url = login_url or settings.LOGIN_URL
    redirect_field_name = redirect_field_name or REDIRECT_FIELD_NAME

    # Handles both original and with object provided permission check
    # as ``obj`` defaults to None

    has_permissions = False
    # global perms check first (if accept_global_perms)
    if accept_global_perms:
        has_permissions = any(request.user.has_perm(perm) for perm in perms) # AQUI EL CAMBIO DE ALL POR ANY
    # if still no permission granted, try obj perms
    if not has_permissions:
        has_permissions = any(request.user.has_perm(perm, obj) # AQUI EL CAMBIO DE ALL POR ANY
                              for perm in perms)

    if not has_permissions:
        if return_403:
            if guardian_settings.RENDER_403:
                response = render(request, guardian_settings.TEMPLATE_403)
                response.status_code = 403
                return response
            elif guardian_settings.RAISE_403:
                raise PermissionDenied
            return HttpResponseForbidden()
        if return_404:
            if guardian_settings.RENDER_404:
                response = render(request, guardian_settings.TEMPLATE_404)
                response.status_code = 404
                return response
            elif guardian_settings.RAISE_404:
                raise ObjectDoesNotExist
            return HttpResponseNotFound()
        else:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(),
                                     login_url,
                                     redirect_field_name)

def cambiable_estado_proyecto(proyecto, newst):
    """
    Verificar si el proyecto puede pasar de su estado actual al estado especificado
    :param proyecto: el proyecto cuyo estado se quiere modificar
    :param newst: nuevo estado del proyecto (in ESTADOS_PROYECTO)
    :return: 'yes' si se puede o <motivo> de por qué no se puede
    """
    currentst = proyecto.estado

    if newst not in ['PENDIENTE', 'EN EJECUCION', 'TERMINADO', 'CANCELADO', 'SUSPENDIDO']:
        return 'no es un estado válido'

    if newst == currentst:
        return 'es el mismo estado'

    if newst == 'PENDIENTE':
        return 'no se puede pasar al estado "PENDIENTE" una vez iniciado o cancelado'

    if newst == 'EN EJECUCION':
        if currentst not in ['PENDIENTE', 'SUSPENDIDO']:
            return 'solo se puede pasar a "EN EJECUCION" si el proyecto está supendido o pendiente'
        elif currentst == 'PENDIENTE':
            return 'yes'
        elif currentst == 'SUSPENDIDO':
            return 'yes'

    if newst == 'TERMINADO':
        if currentst not in ['EN EJECUCION', 'SUSPENDIDO']:
            return 'solo se puede pasar a "TERMINADO" si el proyecto está en ejecución o pendiente'
        elif currentst == 'EN EJECUCION':
            return 'yes'
        elif currentst == 'SUSPENDIDO':
            return 'yes'

    if newst == 'CANCELADO':
        if currentst not in ['PENDIENTE', 'EN EJECUCION', 'SUSPENDIDO']:
            return 'solo se puede pasar a "CANCELADO" si el proyecto está pendiente, en ejecución o suspendido'
        elif currentst == 'PENDIENTE':
            return 'yes'
        elif currentst == 'EN EJECUCION':
            return 'yes'
        elif currentst == 'SUSPENDIDO':
            return 'yes'

    if newst == 'SUSPENDIDO':
        if currentst not in ['EN EJECUCION',]:
            return 'solo se puede pasar a "SUSPENDIDO" si el proyecto está en ejecución'
        elif currentst == 'EN EJECUCION':
            return 'yes'

