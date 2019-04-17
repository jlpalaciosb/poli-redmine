from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden

from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from proyecto.forms import MiembroProyectoForm,EditarMiembroForm
from proyecto.mixins import GuardianAnyPermissionRequiredMixin, ProyectoMixin
from proyecto.models import MiembroProyecto


class MiembroProyectoCreateView(LoginRequiredMixin, GuardianPermissionRequiredMixin, SuccessMessageMixin,
                                CreateView, ProyectoMixin):
    """
    Vista para incorporar un miembro a un proyecto
    """
    model = MiembroProyecto
    template_name = "change_form.html"
    form_class = MiembroProyectoForm
    permission_required = 'proyecto.add_miembroproyecto'
    return_403 = True
    permission_denied_message = 'No tiene permiso para agregar nuevos miembros a este proyecto'

    # guardian va a comprobar que el usuario logueado tiene todos los permisos retornados
    # por get_required_permissions() sobre el objecto que retorna este método
    def get_permission_object(self): return self.get_proyecto()

    def handle_no_permission(self): return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Miembro de Proyecto '{}' incorporado exitosamente.".format(cleaned_data['user'])

    def get_success_url(self):
        return reverse('proyecto_miembro_list',kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(MiembroProyectoCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_miembro_list',kwargs=self.kwargs),
            'proyecto_id': self.kwargs['proyecto_id']
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MiembroProyectoCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Miembro de Proyectos'
        context['titulo_form_crear'] = 'Insertar Datos del Miembro del Proyecto'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.get_proyecto().nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
            {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list',kwargs=self.kwargs)},
            {'nombre': 'Nuevo Miembro', 'url': '#'}
        ]

        return context

class MiembroProyectoListView(LoginRequiredMixin, GuardianAnyPermissionRequiredMixin, TemplateView,
                              ProyectoMixin):
    """
    Vista para listar los miembros de un proyecto. Cualquier usuario que sea miembro del proyecto
    tiene acceso a esta vista
    """
    template_name = 'change_list.html'
    permission_required = (
        'proyecto.add_miembroproyecto',
        'proyecto.change_miembroproyecto',
        'proyecto.delete_miembroproyecto',
    ) # Tiene permiso al tener cualquiera de estos permisos
    return_403 = True
    permission_denied_message = 'No tiene permiso para ver la lista de miembros de este proyecto'

    def get_permission_object(self): return self.get_proyecto()

    def handle_no_permission(self): return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(MiembroProyectoListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Miembros del Proyecto '+ self.get_proyecto().nombre
        context['crear_button'] = self.request.user.has_perm('proyecto.add_miembroproyecto', self.get_permission_object())
        context['crear_url'] = reverse('proyecto_miembro_crear', kwargs=self.kwargs)
        context['crear_button_text'] = 'Nuevo Miembro'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre_de_Usuario', 'Roles']
        context['order'] = [1, "asc"]
        editar_kwargs = self.kwargs.copy()
        editar_kwargs['miembro_id'] = 6436276 # pasamos inicialmente un id aleatorio
        context['datatable_row_link'] = reverse('proyecto_miembro_perfil', kwargs=editar_kwargs)
        context['list_json'] = reverse('proyecto_miembro_list_json', kwargs=kwargs)
        context['miembro_proyecto'] = True

        #Breadcrumbs
        context['breadcrumb'] = [
            {'nombre':'Inicio', 'url':'/'},
            {'nombre':'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.get_proyecto().nombre, 'url': reverse('perfil_proyecto', kwargs=kwargs)},
            {'nombre': 'Miembros', 'url': '#'},
        ]

        return context


class MiembroProyectoListJson(LoginRequiredMixin, GuardianAnyPermissionRequiredMixin,
                              BaseDatatableView, ProyectoMixin):
    """
    Vista que retorna en json la lista de miembros para el datatable
    """
    model = MiembroProyecto
    columns = ['id', 'user', 'roles']
    order_columns = ['', 'user', '']
    permission_required = (
        'proyecto.add_miembroproyecto',
        'proyecto.change_miembroproyecto',
        'proyecto.delete_miembroproyecto',
    ) # Tiene permiso al tener cualquiera de estos permisos
    return_403 = True
    permission_denied_message = 'No tiene permiso para ver la lista de miembros de este proyecto'
    max_display_length = 100

    def get_permission_object(self): return self.get_proyecto()

    def render_column(self, miembro, column):
        if column == 'roles':
            return ', '.join(rol.nombre for rol in miembro.roles.all())
        elif column == 'user':
            return miembro.user.username
        else:
            return super().render_column(miembro, column)

    def get_initial_queryset(self):
        return self.get_proyecto().miembroproyecto_set.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        qs_params = Q(user__username__icontains=search) | Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search)
        return qs.filter(qs_params)

    def ordering(self, qs): return qs.order_by('user__username')


class MiembroProyectoPerfilView(LoginRequiredMixin, GuardianAnyPermissionRequiredMixin, DetailView,
                                ProyectoMixin):
    """
    Vista para el perfil de un miembro de un proyecto. Cualquier usuario que sea miembro del proyecto
    tiene acceso a esta vista
    """
    model = MiembroProyecto
    context_object_name = 'miembro'
    template_name = 'proyecto/miembro/miembro_perfil.html'
    pk_url_kwarg = 'miembro_id'
    permission_required = (
        'proyecto.add_miembroproyecto',
        'proyecto.change_miembroproyecto',
        'proyecto.delete_miembroproyecto',
    ) # Tiene permiso al tener cualquiera de estos permisos
    return_403 = True
    permission_denied_message = 'No tiene permiso para ver el perfil de este miembro de este proyecto'

    def get_permission_object(self): return self.get_proyecto()

    def handle_no_permission(self): return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Perfil del Miembro'

        miembro = context['object']

        # Breadcrumbs
        pid = self.kwargs['proyecto_id']
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.get_proyecto().nombre, 'url': reverse('perfil_proyecto', kwargs={'proyecto_id': pid})},
            {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list', kwargs={'proyecto_id': pid})},
            {'nombre': miembro.user.username, 'url': '#'},
        ]

        context['puedeEditar'] = self.request.user.has_perm('proyecto.change_miembroproyecto', self.get_permission_object())
        context['puedeEliminar'] = self.request.user.has_perm('proyecto.delete_miembroproyecto', self.get_permission_object())

        return context


class MiembroProyectoUpdateView(LoginRequiredMixin, GuardianPermissionRequiredMixin,
                                SuccessMessageMixin, UpdateView, ProyectoMixin):
    """
    Vista que permite modificar los roles de un miembro de proyecto
    """
    model = MiembroProyecto
    form_class = EditarMiembroForm
    context_object_name = 'miembro'
    template_name = 'change_form.html'
    pk_url_kwarg = 'miembro_id'
    permission_required = 'proyecto.change_miembroproyecto'
    return_403 = True
    permission_denied_message = 'No tiene permiso para editar miembros de este proyecto'

    def get_permission_object(self): return self.get_proyecto()

    def handle_no_permission(self): return HttpResponseForbidden()

    def get_success_message(self, cleaned_data): return "Miembro de Proyecto editado exitosamente"

    def get_success_url(self):
        pid = self.kwargs['proyecto_id']
        mid = self.kwargs['miembro_id']
        return reverse('proyecto_miembro_perfil', args=(pid, mid))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MiembroProyectoUpdateView, self).get_context_data(**kwargs)
        p = self.get_proyecto()
        m = MiembroProyecto.objects.get(pk=self.kwargs['miembro_id'])
        context['titulo'] = 'Editar Miembro de Proyecto'
        context['titulo_form_editar'] = 'Datos del Miembro'
        context['titulo_form_editar_nombre'] = m.user.username

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', args=(p.id,))},
            {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list', args=(p.id,))},
            {'nombre': m.user.username, 'url': reverse('proyecto_miembro_perfil', args=(p.id, m.id))},
            {'nombre': 'Editar', 'url': '#'}
        ]

        return context
