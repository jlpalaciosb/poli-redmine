from __future__ import unicode_literals

import threading

from proyecto.models import UserStorySprint
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

import logging
import os

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render
from guardian.conf import settings as guardian_settings

from proyecto.models import UserStorySprint, MiembroProyecto, Sprint

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
        has_permissions = any(request.user.has_perm(perm) for perm in perms)  # AQUI EL CAMBIO DE ALL POR ANY
    # if still no permission granted, try obj perms
    if not has_permissions:
        has_permissions = any(request.user.has_perm(perm, obj)  # AQUI EL CAMBIO DE ALL POR ANY
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
        elif proyecto.sprint_set.filter(estado='EN_EJECUCION').count() > 0:
            return 'tiene un sprint en ejecución'
        elif proyecto.userstory_set.filter(estadoProyecto__in=[1, 3]):
            return 'tiene al menos un user story pendiente o no terminado'
        else:
            return 'yes'

    if newst == 'CANCELADO':
        if currentst not in ['PENDIENTE', 'EN EJECUCION', 'SUSPENDIDO']:
            return 'solo se puede pasar a "CANCELADO" si el proyecto está pendiente, en ejecución o suspendido'
        elif proyecto.sprint_set.filter(estado='EN_EJECUCION').count() > 0:
            return 'tiene un sprint en ejecución'
        else:
            return 'yes'

    if newst == 'SUSPENDIDO':
        if currentst not in ['EN EJECUCION', ]:
            return 'solo se puede pasar a "SUSPENDIDO" si el proyecto está en ejecución'
        elif proyecto.sprint_set.filter(estado='EN_EJECUCION').count() > 0:
            return 'tiene un sprint en ejecución'
        else:
            return 'yes'


class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.from_email = from_email
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.message, self.from_email, self.recipient_list)


def notificar_revision(usp):
    """
    Notifica al scrum master para que revise un user story
    :type usp: UserStorySprint
    """
    sprint = usp.sprint
    proyecto = sprint.proyecto
    assignee = usp.asignee.miembro.user
    scrum_master = proyecto.miembroproyecto_set.filter(roles__nombre='Scrum Master').first().user
    url_revisar = 'http://example.com' + reverse('sprint_us_ver', args=(proyecto.id, sprint.id, usp.id))
    EmailThread(
        'Revisión del User Story: "%s"' % usp.us.nombre,
        'El miembro "%s" finalizó el user story "%s". Por favor, revise el user story para aceptar '
        'o rechazar su culminación. Siga el siguiente enlace para tal efecto: %s' %
        (assignee.get_full_name(), usp.us.nombre, url_revisar),
        settings.EMAIL_HOST_USER, [scrum_master.email, ],
    ).start()


def notificar_asignacion(usp):
    """
    Cuando se agrega un user story a un sprint, se le notifica al asignado del user story
    :type usp: UserStorySprint
    """
    sprint = usp.sprint
    proyecto = sprint.proyecto
    assignee = usp.asignee.miembro.user
    url_ver = 'http://example.com' + reverse('sprint_us_ver', args=(proyecto.id, sprint.id, usp.id))
    EmailThread(
        'Asignación del User Story: "%s"' % usp.us.nombre,
        'Le asignaron el user story "%s" para el sprint %d del proyecto "%s". Le notificaremos cuando '
        'inicie el sprint. Siga el siguiente enlace para ver los detalles del user story: %s' %
        (usp.us.nombre, sprint.orden, proyecto.nombre, url_ver),
        settings.EMAIL_HOST_USER, [assignee.email, ]
    ).start()


def notificar_nuevo_miembro(miembro):
    """
    Se le notifica al usuario cuando se le agrega como miembro de un proyecto
    :type miembro: MiembroProyecto
    """
    url_ver = 'http://example.com' + reverse('perfil_proyecto', args=(miembro.proyecto.id,))
    proyecto = miembro.proyecto
    EmailThread(
        'Nuevo Miembro del Proyecto: "%s"' % proyecto.nombre,
        'Ahora usted es miembro del proyecto "%s". Siga el siguiente enlace para ver el '
        'proyecto: %s' % (proyecto.nombre, url_ver),
        settings.EMAIL_HOST_USER, [miembro.user.email, ]
    ).start()


def notificar_aceptacion(usp):
    """
    Se le notifica al usuario cuando su user story se acepta
    :type usp: UserStorySprint
    """
    assignee = usp.asignee.miembro.user
    EmailThread(
        'Aceptación del User Story: "%s"' % usp.us.nombre,
        'Su user story "%s" fue aceptado por el scrum master.' % (usp.us.nombre,),
        settings.EMAIL_HOST_USER, [assignee.email, ]
    ).start()


def notificar_rechazo(usp):
    """
    Se le notifica al usuario cuando su user story se rechaza
    :type usp: UserStorySprint
    """
    sprint = usp.sprint
    proyecto = sprint.proyecto
    assignee = usp.asignee.miembro.user
    url_ver = 'http://example.com' + reverse('sprint_us_ver', args=(proyecto.id, sprint.id, usp.id))
    EmailThread(
        'Rechazo del User Story: "%s"' % usp.us.nombre,
        'Su user story "%s" fue rechazado por el scrum master. Entre las actividades del user story '
        'podrá ver la nota del rechazo. Siga el siguiente enlace para ver la página del user story '
        'en el sprint: %s' % (usp.us.nombre, url_ver),
        settings.EMAIL_HOST_USER, [assignee.email, ]
    ).start()

def notificar_inicio_sprint(sprint):
    """
    Notifica a todos los miembros del sprint que el sprint acaba de iniciar. Detalla a cada miembro
    los user stories que le fueron asignados.
    :type sprint: Sprint
    :return:
    """
    subject = 'Inicio del sprint %d del proyecto "%s"' % (sprint.orden, sprint.proyecto.nombre)
    url_sprint = 'http://example.com' + reverse('proyecto_sprint_administrar',
                                                args=(sprint.proyecto.id, sprint.id))
    for miembro_sprint in sprint.miembrosprint_set.all():
        usps_asignados = miembro_sprint.userstorysprint_set.all()
        uss_asignados = list(map(lambda usp: usp.us, usps_asignados))
        uss_asignados_string = 'No le asignaron ningún user story para este sprint. \n'
        if len(uss_asignados) > 0:
            uss_asignados_string = 'Le asignaron los siguientes user stories para este sprint: \n'
            for us in uss_asignados: uss_asignados_string += ' - %s\n' % us.nombre

        EmailThread(
            subject,
            'El sprint del cual usted es miembro acaba de iniciar. Siga el siguiente enlace para '
            'ver la página del sprint: %s' % url_sprint + '\n\n' + uss_asignados_string,
            settings.EMAIL_HOST_USER, [miembro_sprint.miembro.user.email,]
        ).start()
