from django.http import HttpResponseForbidden
from django.utils.html import escape
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse,reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.models import User, Group
from proyecto.models import RolProyecto
from .forms import UsuarioForm, EditarUsuarioForm
from ProyectoIS2_9.utils import cualquier_permiso, es_administrador


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
            'id', 'Username', 'Correo Electrónico'
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
    columns = ['id', 'username', 'email']
    order_columns = ['id', 'username', 'email']
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


class UsuarioUpdateView(SuccessMessageMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditarUsuarioForm
    context_object_name = 'usuario'
    template_name = 'change_form.html'
    pk_url_kwarg = 'user_id'
    permission_required = 'proyecto.change_usuario'
    
    def has_permission(self):
        usr_edit = self.get_object()
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
            {'nombre': context['usuario'].username, 'url': reverse('usuario:ver',kwargs=self.kwargs)},
            {'nombre': 'Editar', 'url': '#'},
        ]

        return context

    def form_valid(self, form):
        usuario = form.instance
        password = form.cleaned_data['contraseña']
        roles_proyecto = RolProyecto.objects.filter(id__in=list(map(lambda x:x['id'],list(usuario.groups.all().values('id')))))
        if password:
            usuario.set_password(password)
        response = super().form_valid(form)
        for rol in roles_proyecto:
            usuario.groups.add(rol)
        return response


class UsuarioPerfilView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'usuario'
    template_name = 'usuario/change_perfil.html'
    pk_url_kwarg = 'user_id'
    permission_required = ('proyecto.add_usuario','proyecto.change_usuario','proyecto.delete_usuario')

    def has_permission(self):
        usr_ver = self.get_object()
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
        usr_elim = self.get_object()
        if usr_elim.miembroproyecto_set.all().count() > 0:
            return 'es miembro de al menos un proyecto'
        if usr_elim == self.request.user:
            return 'es usted mismo'
        if es_administrador(usr_elim) and Group.objects.filter(name='Administrador').count() == 1:
            return 'es el único que tiene el rol de Administrador'

        return 'Yes'

    def delete(self, request, *args, **kwargs):
        if self.eliminable() != 'Yes':
            return HttpResponseForbidden()
        return super().delete(request, *args, **kwargs)
