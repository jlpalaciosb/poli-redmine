from django.http import HttpResponseForbidden
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

from proyecto.forms import USForm, ActividadForm
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoEstadoInvalidoMixin
from proyecto.models import Proyecto, Sprint, UserStory, UserStorySprint, Actividad


class ActividadBaseView(LoginRequiredMixin):
    proyecto = None
    sprint = None
    usp = None
    actividad = None

    def dispatch(self, request, *args, **kwargs):
        self.proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        self.sprint = Sprint.objects.get(pk=kwargs['sprint_id'])
        self.usp = UserStorySprint.objects.get(pk=kwargs['usp_id'])
        return super().dispatch(request, *args, **kwargs)


class ActividadCreateView(SuccessMessageMixin, ActividadBaseView, PermissionRequiredMixin, CreateView):
    """
    Vista para agregar una Actividad a un User Story en un Sprint
    """
    model = Actividad
    template_name = "change_form.html"
    form_class = ActividadForm

    def has_permission(self):
        return self.usp.asignee.miembro.user == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Actividad agregada exitosamente"

    def get_success_url(self):
        return reverse('actividad_list', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': reverse('actividad_list', kwargs=self.kwargs),
            'usp': self.usp,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar Actividad'
        context['titulo_form_crear'] = 'Insertar Datos de la Actividad'
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.proyecto.id,))},
            {'nombre': 'Sprint %d' % self.sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': self.usp.us.nombre, 'url': reverse('sprint_us_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': 'Actividades', 'url': reverse('actividad_list', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': 'Agregar', 'url': '#'},
        ]
        return context


class ActividadListView(ActividadBaseView, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para ver las actividades de un User Story en un Sprint
    """
    template_name = 'change_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo'] = 'Actividades'

        if self.usp.asignee.miembro.user == self.request.user:
            context['crear_button'] = True
            context['crear_url'] = reverse('actividad_agregar', kwargs=self.kwargs)
            context['crear_button_text'] = 'Agregar Actividad'

        # datatable
        context['nombres_columnas'] = ['id', 'Nombre', 'Fecha']
        context['order'] = [2, "desc"]
        context['actividad'] = True
        ver_kwargs = self.kwargs.copy()
        ver_kwargs['actividad_id'] = 7495261  # pasamos inicialmente un id aleatorio
        context['datatable_row_link'] = reverse('index') # reverse('actividad_ver', kwargs=ver_kwargs)
        context['list_json'] = reverse('actividad_list_json', kwargs=kwargs)

        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.proyecto.id,))},
            {'nombre': 'Sprint %d' % self.sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': self.usp.us.nombre, 'url': reverse('sprint_us_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': 'Actividades', 'url': '#'},
        ]

        return context


class ActividadListJsonView(ActividadBaseView, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista que retorna en json la lista de las actividades de un user story en un sprint
    """
    model = Actividad
    columns = ['id', 'nombre', 'fechaHora']
    order_columns = ['', '', 'fechaHora']
    max_display_length = 100

    def get_initial_queryset(self):
        return Actividad.objects.filter(usSprint=self.usp)


class USPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
    Vista para ver los datos básicos de un User Story a nivel de proyecto
    """
    model = UserStory
    context_object_name = 'us'
    template_name = 'proyecto/us/us_perfil.html'
    pk_url_kwarg = 'us_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        us = context['object']

        context['titulo'] = 'Ver US'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', args=(p.id,))},
            {'nombre': 'Product Backlog', 'url': reverse('proyecto_us_list', args=(p.id,))},
            {'nombre': us.nombre, 'url': '#'},
        ]

        context['puedeEditar'] = self.request.user.has_perm('proyecto.change_us', p)

        return context


class USUpdateView(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEstadoInvalidoMixin, UpdateView):
    """
    Vista que permite modificar los datos básicos de un User Story a nivel proyecto
    """
    model = UserStory
    form_class = USForm
    template_name = 'change_form.html'
    pk_url_kwarg = 'us_id'
    permission_required = 'proyecto.change_us'
    estados_inaceptables = ['PENDIENTE', 'TERMINADO', 'SUSPENDIDO', 'CANCELADO']

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "US editado exitosamente"

    def get_success_url(self):
        pid = self.kwargs['proyecto_id']
        uid = self.kwargs['us_id']
        return reverse('proyecto_us_ver', args=(pid, uid))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
            'creando': False,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        us = context['object']

        context['titulo'] = 'Editar Datos del US'
        context['titulo_form_editar'] = 'US'
        context['titulo_form_editar_nombre'] = us.nombre

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', args=(p.id,))},
            {'nombre': 'Product Backlog', 'url': reverse('proyecto_us_list', args=(p.id,))},
            {'nombre': us.nombre, 'url': reverse('proyecto_us_ver', args=(p.id, us.id))},
            {'nombre': 'Editar', 'url': '#'}
        ]

        return context
