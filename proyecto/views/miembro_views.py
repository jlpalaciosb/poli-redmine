from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden

from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from proyecto.forms import CrearMiembroForm, EditarMiembroForm
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin
from proyecto.models import MiembroProyecto, Proyecto


class MiembroProyectoCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, CreateView):
    """
    Vista para incorporar un miembro a un proyecto
    """
    model = MiembroProyecto
    template_name = "change_form.html"
    form_class = CrearMiembroForm
    permission_required = 'proyecto.add_miembroproyecto'

    def handle_no_permission(self):
        return HttpResponseForbidden()

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
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])

        context = super(MiembroProyectoCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Miembro de Proyectos'
        context['titulo_form_crear'] = 'Insertar Datos del Miembro del Proyecto'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
            {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list', kwargs=self.kwargs)},
            {'nombre': 'Crear Miembro', 'url': '#'}
        ]

        return context


class MiembroProyectoListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar los miembros de un proyecto. Cualquier usuario que sea miembro del proyecto
    tiene acceso a esta vista
    """
    template_name = 'change_list.html'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])

        context = super(MiembroProyectoListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Miembros del Proyecto '+ p.nombre
        context['crear_button'] = self.request.user.has_perm('proyecto.add_miembroproyecto', p)
        context['crear_url'] = reverse('proyecto_miembro_crear', kwargs=self.kwargs)
        context['crear_button_text'] = 'Crear Miembro'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre_de_Usuario', 'Roles']
        context['order'] = [1, "asc"]
        editar_kwargs = self.kwargs.copy(); editar_kwargs['miembro_id'] = 6436276 # pasamos inicialmente un id aleatorio
        context['datatable_row_link'] = reverse('proyecto_miembro_perfil', kwargs=editar_kwargs)
        context['list_json'] = reverse('proyecto_miembro_list_json', kwargs=kwargs)
        context['miembro_proyecto'] = True

        #Breadcrumbs
        context['breadcrumb'] = [
            {'nombre':'Inicio', 'url':'/'},
            {'nombre':'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', kwargs=kwargs)},
            {'nombre': 'Miembros', 'url': '#'},
        ]

        return context


class MiembroProyectoListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista que retorna en json la lista de miembros para el datatable
    """
    model = MiembroProyecto
    columns = ['id', 'user', 'roles']
    order_columns = ['', 'user', '']
    max_display_length = 100

    def render_column(self, miembro, column):
        if column == 'roles':
            return ', '.join(rol.nombre for rol in miembro.roles.all())
        elif column == 'user':
            return miembro.user.username
        else:
            return super().render_column(miembro, column)

    def get_initial_queryset(self):
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        return p.miembroproyecto_set.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        qs_params = Q(user__username__icontains=search) | Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search)
        return qs.filter(qs_params)

    def ordering(self, qs): return qs.order_by('user__username')


class MiembroProyectoPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
    Vista para el perfil de un miembro de un proyecto. Cualquier usuario que sea miembro del proyecto
    tiene acceso a esta vista
    """
    model = MiembroProyecto
    context_object_name = 'miembro'
    template_name = 'proyecto/miembro/miembro_perfil.html'
    pk_url_kwarg = 'miembro_id'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        m = context['object']

        context['titulo'] = 'Perfil del Miembro'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', args=(p.id,))},
            {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list', args=(p.id,))},
            {'nombre': m.user.username, 'url': '#'},
        ]

        context['puedeEditar'] = self.request.user.has_perm('proyecto.change_miembroproyecto', p)
        context['puedeEliminar'] = self.request.user.has_perm('proyecto.delete_miembroproyecto', p)
        # True si el usuario logueado es scrum master en el proyecto
        context['isSM'] = True

        return context


class MiembroProyectoUpdateView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, UpdateView):
    """
    Vista que permite modificar los roles de un miembro de proyecto
    """
    model = MiembroProyecto
    form_class = EditarMiembroForm
    context_object_name = 'miembro'
    template_name = 'change_form.html'
    pk_url_kwarg = 'miembro_id'
    permission_required = 'proyecto.change_miembroproyecto'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Roles del miembro editado exitosamente"

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
        context = super().get_context_data(**kwargs)

        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        m = context['object']

        context['titulo'] = 'Editar Roles del Miembro'
        context['titulo_form_editar'] = 'Miembro de Proyecto'
        context['titulo_form_editar_nombre'] = m.user.username

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', args=(p.id,))},
            {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list', args=(p.id,))},
            {'nombre': m.user.username, 'url': reverse('proyecto_miembro_perfil', args=(p.id, m.id))},
            {'nombre': 'Editar Roles', 'url': '#'}
        ]

        return context
