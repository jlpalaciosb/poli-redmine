"""
django-guardian helper functions.

Functions defined within this module should be considered as django-guardian's
internal functionality. They are **not** guaranteed to be stable - which means
they actual input parameters/output type may change in future releases.
"""
from __future__ import unicode_literals

import logging
import os
from itertools import chain

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Model, QuerySet
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render
from guardian.conf import settings as guardian_settings
from guardian.ctypes import get_content_type
from guardian.exceptions import NotUserNorGroup

logger = logging.getLogger(__name__)
abspath = lambda *p: os.path.abspath(os.path.join(*p))


# retorna true si el usuario tiene uno de los permisos
def cualquier_permiso(user, perms):
    for perm in perms:
        if user.has_perm(perm):
            return True
    return False


def get_40x_or_None_ANY(request, perms, obj=None, login_url=None,
                    redirect_field_name=None, return_403=False,
                    return_404=False, accept_global_perms=False):
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

