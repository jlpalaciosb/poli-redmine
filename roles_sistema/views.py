from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse

from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.views.generic.base import ContextMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic.edit import FormView
from django_datatables_view.base_datatable_view import BaseDatatableView
from datetime import datetime

from proyecto.forms import ProyectoForm
from proyecto.models import RolAdministrativo

class RolListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(RolListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Roles Administrativo'
        context['crear_button'] = True
        context['crear_url'] = '#'
        context['crear_button_text'] = 'Nuevo Rol'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = '#'  # pasamos inicialmente el id 1
        context['list_json'] = reverse('rol_sistema:lista_json')

        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Rol Administrativo', 'url': '#'},
                   ]



        return context

class RolListJson(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    model = RolAdministrativo
    columns = ['id', 'name']
    order_columns = ['id', 'name']
    max_display_length = 100
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'