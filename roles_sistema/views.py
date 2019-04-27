from django.http import HttpResponseForbidden
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse,reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponseRedirect
from datos_de_prueba.funciones import ROL_ADMINISTRADOR_NOMBRE
from roles_sistema.forms import RolSistemaForm
from proyecto.models import RolAdministrativo
from ProyectoIS2_9.utils import cualquier_permiso

class RolListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = (
        'proyecto.add_roladministrativo', 'proyecto.change_roladministrativo', 'proyecto.delete_roladministrativo'
    )
    permission_denied_message = 'No tiene permiso para ver los roles.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def has_permission(self):
        """
        Se sobreescribe para que si tiene al menos uno de los permisos listados en permission_required, tiene permisos
        :return:
        """
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def get_context_data(self, **kwargs):
        context = super(RolListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Roles Administrativos'
        context['crear_button'] = self.request.user.has_perm('proyecto.add_roladministrativo')
        context['crear_url'] = reverse('rol_sistema:crear')
        context['crear_button_text'] = 'Nuevo Rol'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('rol_sistema:ver', args=(1,))  # pasamos inicialmente el id 1
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
    permission_required = (
        'proyecto.add_roladministrativo', 'proyecto.change_roladministrativo', 'proyecto.delete_roladministrativo'
    )
    permission_denied_message = 'No tiene permiso para ver los roles.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())


class RolCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = RolAdministrativo
    template_name = "change_form.html"
    form_class = RolSistemaForm
    permission_required = 'proyecto.add_roladministrativo'
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
    permission_required = 'proyecto.change_roladministrativo'
    permission_denied_code = None
    permission_denied_message = 'No tiene permiso para Editar Roles'

    def has_permission(self):
        """
        Se sobreescribe la comprobacion de permisos para denegar el acceso si el usuario posee el rol administrativo a editar
        :return:
        """
        try:
            rol_a_editar = self.get_object()
            roles_usuario = RolAdministrativo.objects.filter(user=self.request.user)

            if rol_a_editar.name == ROL_ADMINISTRADOR_NOMBRE:
                self.permission_denied_code = 'ROL_ADMINISTRADOR'
            elif rol_a_editar in roles_usuario:
                self.permission_denied_code = 'PROPIO_ROL'

            if self.permission_denied_code is not None:
                return False
        except RolAdministrativo.DoesNotExist:
            return super(RolUpdateView, self).has_permission()
        except:
            return super(RolUpdateView, self).has_permission()

        return super(RolUpdateView, self).has_permission()

    def handle_no_permission(self):
        if self.permission_denied_code == 'PROPIO_ROL':
            messages.add_message(self.request, messages.WARNING, 'No puede editar este rol porque es su rol')
        elif self.permission_denied_code == 'ROL_ADMINISTRADOR':
            messages.add_message(self.request, messages.WARNING, 'No puede editar este rol porque es el rol por defecto Administrador')

        if self.permission_denied_code is None:
            return HttpResponseForbidden()
        else:
            return HttpResponseRedirect(reverse('rol_sistema:ver', kwargs=self.kwargs))

    def get_success_message(self, cleaned_data):
        return "Rol Administrativo '{}' editado exitosamente.".format(cleaned_data['name'])

    def get_success_url(self):
        return reverse('rol_sistema:ver', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(RolUpdateView, self).get_form_kwargs()

        kwargs.update({
            'success_url': self.get_success_url(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RolUpdateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Editar Rol Administrativo'
        context['titulo_form_editar'] = 'Datos del Rol'
        context['titulo_form_editar_nombre'] = context[RolUpdateView.context_object_name].name

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Roles Administrativos', 'url': reverse('rol_sistema:lista')},
                                 {'nombre': context['rol'].name, 'url': reverse('rol_sistema:ver',kwargs=self.kwargs)},
                                 {'nombre': 'Editar', 'url': '#'},
                                 ]

        return context

class RolPerfilView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = RolAdministrativo
    context_object_name = 'rol'
    template_name = 'roles_sistema/change_perfil.html'
    pk_url_kwarg = 'rol_id'
    permission_required = ('proyecto.add_roladministrativo','proyecto.change_roladministrativo','proyecto.delete_roladministrativo')
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def get_context_data(self, **kwargs):
        context = super(RolPerfilView, self).get_context_data(**kwargs)
        context['titulo'] = 'Perfil del Rol Administrativo'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Roles Administrativos', 'url': reverse('rol_sistema:lista')},
                                 {'nombre': context['rol'].name, 'url': '#'}
                                 ]
        rol = self.get_object()
        context['es_rol_administrador'] = rol.name == ROL_ADMINISTRADOR_NOMBRE

        return context


class RolEliminarView(LoginRequiredMixin, PermissionRequiredMixin,SuccessMessageMixin, DeleteView):
    model = RolAdministrativo
    context_object_name = 'rol'
    template_name = 'roles_sistema/eliminar_rol.html'
    pk_url_kwarg = 'rol_id'
    permission_required = 'proyecto.delete_roladministrativo'
    permission_denied_code = None
    permission_denied_message = 'No tiene permiso para eliminar el rol.'
    success_url = reverse_lazy('rol_sistema:lista')

    def has_permission(self):
        """
        Se sobreescribe la comprobacion de permisos para denegar el acceso si hay algun usuario que posea el rol administrativo a eliminar o es el rol administrador
        :return:
        """
        try:
            rol_a_eliminar = self.get_object()
            roles_usuario = RolAdministrativo.objects.filter(user=self.request.user)

            if rol_a_eliminar.name == ROL_ADMINISTRADOR_NOMBRE:
                self.permission_denied_code = 'ROL_ADMINISTRADOR'
            elif rol_a_eliminar in roles_usuario:
                self.permission_denied_code = 'PROPIO_ROL'
            elif rol_a_eliminar.user_set.all():
                self.permission_denied_code = 'USADO'

            if self.permission_denied_code is not None:
                return False
        except RolAdministrativo.DoesNotExist:
            return super(RolEliminarView, self).has_permission()
        except:
            return super(RolEliminarView, self).has_permission()
        else:
            return super(RolEliminarView, self).has_permission()

    def handle_no_permission(self):
        if self.permission_denied_code == 'PROPIO_ROL':
            messages.add_message(self.request, messages.WARNING, 'No puede eliminar este rol porque es su rol')
        elif self.permission_denied_code == 'USADO':
            messages.add_message(self.request, messages.WARNING, 'No puede eliminar este rol porque hay al menos un usuario con el rol')
        elif self.permission_denied_code == 'ROL_ADMINISTRADOR':
            messages.add_message(self.request, messages.WARNING, 'No puede eliminar este rol porque es el rol por defecto Administrador')

        if self.permission_denied_code is None:
            return HttpResponseForbidden()
        else:
            return HttpResponseRedirect(reverse('rol_sistema:ver', kwargs=self.kwargs))

    def get_success_message(self, cleaned_data):
        return "Rol Administrativo  eliminado exitosamente."

    def get_context_data(self, **kwargs):
        context = super(RolEliminarView, self).get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Rol'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Roles Administrativos', 'url': reverse('rol_sistema:lista')},
                                 {'nombre': context['rol'].name,
                                  'url': reverse('rol_sistema:ver', kwargs=self.kwargs)},
                                 {'nombre': 'Eliminar', 'url': '#'}, ]
        return context

    def delete(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.SUCCESS, 'Rol Administrativo Eliminado')
        return super().delete(request, *args, **kwargs)
