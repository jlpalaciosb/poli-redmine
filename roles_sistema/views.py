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

from roles_sistema.forms import RolSistemaForm
from proyecto.models import RolAdministrativo

class RolListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(RolListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Roles Administrativos'
        context['crear_button'] = True
        context['crear_url'] = reverse('rol_sistema:crear')
        context['crear_button_text'] = 'Nuevo Rol'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('rol_sistema:editar', args=(1,))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('rol_sistema:lista_json')

        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Roles Administrativos', 'url': '#'},
                   ]



        return context

class RolListJson(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    model = RolAdministrativo
    columns = ['id', 'name']
    order_columns = ['id', 'name']
    max_display_length = 100
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

class RolCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = RolAdministrativo
    template_name = "change_form.html"
    form_class = RolSistemaForm
    permission_required = 'proyecto.add_proyecto'
    permission_denied_message = 'No tiene permiso para Crear nuevos proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Rol '{}' creado exitosamente.".format(cleaned_data['name'])

    def get_success_url(self):
        return reverse('rol_sistema:lista')

    def get_form_kwargs(self):
        kwargs = super(RolCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('rol_sistema:lista'),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RolCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Roles Administrativos'
        context['titulo_form_crear'] = 'Insertar Datos del Nuevo Rol Administrativo'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Roles Administrativos', 'url': reverse('rol_sistema:lista')},
                                 {'nombre': 'Crear', 'url': '#'}
                                 ]

        return context

class RolUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = RolAdministrativo
    form_class = RolSistemaForm
    context_object_name = 'rol'
    template_name = 'change_form.html'
    pk_url_kwarg = 'rol_id'
    permission_required = 'proyecto.change_proyecto'
    permission_denied_message = 'No tiene permiso para Editar Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Rol Administrativo '{}' editado exitosamente.".format(cleaned_data['name'])

    def get_success_url(self):
        return reverse('rol_sistema:lista')

    def get_form_kwargs(self):
        kwargs = super(RolUpdateView, self).get_form_kwargs()

        kwargs.update({
            'success_url': self.get_success_url(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RolUpdateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Rol Administrativo'
        context['titulo_form_editar'] = 'Datos del Rol'
        context['titulo_form_editar_nombre'] = context[RolUpdateView.context_object_name].name

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Roles Administrativos', 'url': reverse('rol_sistema:lista')},
                                 {'nombre': context['rol'].name, 'url': '#'},
                                 {'nombre': 'Editar', 'url': '#'},
                                 ]

        return context





