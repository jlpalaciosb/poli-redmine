from django.http import HttpResponseForbidden
from django.utils.html import escape
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse,reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.models import User

from .forms import UsuarioForm
from ProyectoIS2_9.utils import cualquier_permiso


class UsuarioListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = ('proyecto.add_usuario','proyecto.change_usuario','proyecto.delete_usuario')

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def has_permission(self):
        """
        Se sobreescribe para que si tiene al menos uno de los permisos listados en permission_required, tiene permisos
        """
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def get_context_data(self, **kwargs):
        context = super(UsuarioListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Usuarios'
        context['crear_button'] = self.request.user.has_perm('proyecto.add_usuario')
        context['crear_url'] = reverse('usuario:crear')
        context['crear_button_text'] = 'Nuevo Usuario'

        # datatables
        context['nombres_columnas'] = [
            'id', 'Username', 'Nombres y Apellidos', 'Correo Electrónico'
        ]
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('usuario:ver', args=(1,))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('usuario:lista_json')

        #Breadcrumbs
        context['breadcrumb'] = [
            {'nombre':'Inicio', 'url':'/'},
            {'nombre':'Usuarios', 'url': '#'},
        ]

        return context


class UsuarioListJson(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    model = User
    columns = ['id', 'username', 'nombres y apellidos', 'email']
    order_columns = ['id', 'username', 'nombres y apellidos', 'email']
    max_display_length = 100
    permission_required = ('proyecto.add_usuario', 'proyecto.change_usuario', 'proyecto.delete_usuario')

    def get_initial_queryset(self):
        """
        Se excluyen del listado a todos los que son superusuario o tienen acceso al django admin
        """
        return User.objects.all().exclude(is_superuser=True).exclude(is_staff=True)

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'nombres y apellidos':
            # escape HTML for security reasons
            return escape(row.get_full_name())
        else:
            return super(UsuarioListJson, self).render_column(row, column)


class UsuarioCreateView(SuccessMessageMixin, PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = User
    template_name = "change_form.html"
    form_class = UsuarioForm
    permission_required = 'proyecto.add_usuario'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Usuario '{}' creado exitosamente.".format(cleaned_data['username'])

    def get_success_url(self):
        return reverse('usuario:lista')

    def get_form_kwargs(self):
        kwargs = super(UsuarioCreateView, self).get_form_kwargs()
        kwargs.update({'success_url': reverse('usuario:lista')})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UsuarioCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Usuario'
        context['titulo_form_crear'] = 'Insertar Datos del Nuevo Usuario'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Usuarios', 'url': reverse('usuario:lista')},
            {'nombre': 'Crear', 'url': '#'}
        ]

        return context

    def form_valid(self, form):
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
    permission_required = 'proyecto.change_usuario'
    
    def has_permission(self):
        usr_edit = self.get_object()
        # nunca se puede editar superuser o staff
        if usr_edit.is_staff or usr_edit.is_superuser: return False
        return super().has_permission()

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Usuario '{}' editado exitosamente.".format(cleaned_data['username'])

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
        context['titulo'] = 'Editar Usuario'
        context['titulo_form_editar'] = 'Datos del Usuario'
        context['titulo_form_editar_nombre'] = context[UsuarioUpdateView.context_object_name].username

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Usuarios', 'url': reverse('usuario:lista')},
            {'nombre': context['usuario'].get_full_name, 'url': reverse('usuario:ver',kwargs=self.kwargs)},
            {'nombre': 'Editar', 'url': '#'},
        ]

        return context

    def form_valid(self, form):
        usuario = form.save(commit=False)
        if not form.instance.pk:
            usuario.set_password(usuario.password)
        elif usuario.password:
            usuario.set_password(usuario.password)
        else:
            usuario.password = User.objects.get(pk=usuario.id).password

        return super().form_valid(form)


class UsuarioPerfilView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'usuario'
    template_name = 'usuario/change_perfil.html'
    pk_url_kwarg = 'user_id'
    permission_required = ('proyecto.add_usuario','proyecto.change_usuario','proyecto.delete_usuario')

    def has_permission(self):
        usr_ver = self.get_object()
        # nunca se puede ver superuser o staff
        if usr_ver.is_staff or usr_ver.is_superuser: return False
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(UsuarioPerfilView, self).get_context_data(**kwargs)

        context['titulo'] = 'Perfil del Usuario'

        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Usuarios', 'url': reverse('usuario:lista')},
            {'nombre': context['usuario'].username, 'url': '#'}
        ]

        return context


class UsuarioEliminarView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    context_object_name = 'usuario'
    template_name = 'usuario/eliminar_usuario.html'
    pk_url_kwarg = 'user_id'
    permission_required = 'proyecto.delete_usuario'
    success_url = reverse_lazy('usuario:lista')

    def has_permission(self):
        usr_delete = self.get_object()
        # nunca se puede eliminar superuser o staff
        if usr_delete.is_staff or usr_delete.is_superuser: return False
        return super().has_permission()

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Usuario eliminado exitosamente."

    def get_context_data(self, **kwargs):
        context = super(UsuarioEliminarView, self).get_context_data(**kwargs)

        context['titulo'] = 'Eliminar Usuario'

        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Usuarios', 'url': reverse('usuario:lista')},
            {'nombre': context['usuario'].username, 'url': reverse('usuario:ver', kwargs=self.kwargs)},
            {'nombre': 'Eliminar', 'url': '#'}
        ]

        eliminable = self.eliminable()
        if eliminable == 'Yes':
            context['eliminable'] = True
        else:
            context['eliminable'] = False
            context['motivo'] = eliminable

        return context

    def eliminable(self):
        """
        Si un usuario es miembro de algun proyecto entonces no se puede eliminar. No hace falta
        otras condiciones como si tiene algun US o algo así, porque en tal caso sí o sí estaría
        en un proyecto
        :return 'Yes' si es posible o <motivo> de por qué no se puede eliminar
        """
        if self.get_object().miembroproyecto_set.all().count() > 0:
            return 'el usuario es miembro de al menos un proyecto'
        if self.get_object() == self.request.user:
            return 'el usuario es usted mismo'
        return 'Yes'

    def delete(self, request, *args, **kwargs):
        if self.eliminable() != 'Yes':
            return HttpResponseForbidden()
        return super().delete(request, *args, **kwargs)
