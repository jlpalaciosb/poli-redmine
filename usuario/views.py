from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.utils.html import escape
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.views.generic.base import ContextMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic.edit import FormView
from django_datatables_view.base_datatable_view import BaseDatatableView
from datetime import datetime

from .forms import UsuarioForm
from django.contrib.auth.models import User

class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(UsuarioListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Usuarios'
        context['crear_button'] = True
        context['crear_url'] = reverse('usuario:crear')
        context['crear_button_text'] = 'Nuevo Usuario'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre','Email']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('usuario:ver', args=(1,))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('usuario:lista_json')

        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Usuarios', 'url': '#'},
                   ]



        return context

class UsuarioListJson(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    model = User
    columns = ['id', 'username','email']
    order_columns = ['id', 'username','email']
    max_display_length = 100
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'username':
            # escape HTML for security reasons
            return escape('{0} {1}'.format(row.first_name, row.last_name))
        else:
            return super(UsuarioListJson, self).render_column(row, column)


    def get_initial_queryset(self):
        """
        Se sobreescribe el metodo para que la lista sean todos los usuarios que no sean Anonymous User
        :return:
        """
        return self.model.objects.exclude(username='AnonymousUser')

class UsuarioCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    template_name = "change_form.html"
    form_class = UsuarioForm
    permission_required = 'proyecto.add_proyecto'
    permission_denied_message = 'No tiene permiso para Crear nuevos proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Usuario '{}' creado exitosamente.".format(cleaned_data['username'])

    def get_success_url(self):
        return reverse('usuario:lista')

    def get_form_kwargs(self):
        kwargs = super(UsuarioCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('usuario:lista')
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UsuarioCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Usuario'
        context['titulo_form_crear'] = 'Insertar Datos del Nuevo Usuario'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Usuarios', 'url': reverse('usuario:lista')},
                                 {'nombre': 'Crear', 'url': '#'}
                                 ]

        return context

    def form_valid(self, form):
        """

        :param form:
        :return:
        """
        usuario = form.save(commit=False)
        if not form.instance.pk:
            usuario.set_password(usuario.password)


        return super().form_valid(form)


class UsuarioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UsuarioForm
    context_object_name = 'usuario'
    template_name = 'change_form.html'
    pk_url_kwarg = 'user_id'
    permission_required = 'proyecto.change_proyecto'
    permission_denied_message = 'No tiene permiso para Editar Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Rol Administrativo '{}' editado exitosamente.".format(cleaned_data['username'])

    def get_success_url(self):
        return reverse('usuario:ver', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(UsuarioUpdateView, self).get_form_kwargs()

        kwargs.update({
            'success_url': self.get_success_url()
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UsuarioUpdateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Usuario'
        context['titulo_form_editar'] = 'Datos del Usuario'
        context['titulo_form_editar_nombre'] = context[UsuarioUpdateView.context_object_name].username

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Usuarios', 'url': reverse('usuario:lista')},
                                 {'nombre': context['usuario'].get_full_name, 'url': reverse('usuario:ver',kwargs=self.kwargs)},
                                 {'nombre': 'Editar', 'url': '#'},
                                 ]

        return context

    def form_valid(self, form):
        """

        :param form:
        :return:
        """
        usuario = form.save(commit=False)
        if not form.instance.pk:
            usuario.set_password(usuario.password)
        elif usuario.password:
            usuario.set_password(usuario.password)
        else:
            usuario.password = User.objects.get(pk=usuario.id).password

        return super().form_valid(form)

class UsuarioPerfilView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = User
    context_object_name = 'usuario'
    template_name = 'usuario/change_perfil.html'
    pk_url_kwarg = 'user_id'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(UsuarioPerfilView, self).get_context_data(**kwargs)
        context['titulo'] = 'Perfil del Rol'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Usuarios', 'url': reverse('usuario:lista')},
                                 {'nombre': context['usuario'].get_full_name(), 'url': '#'}
                                 ]

        return context


