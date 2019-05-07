from django.http import HttpResponseForbidden
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
import pytz

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
        if 'actividad_id' in kwargs:
            self.actividad = Actividad.objects.get(pk=kwargs['actividad_id'])
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
        context['nombres_columnas'] = ['id', 'Nombre', 'Fecha', 'Responsable']
        context['order'] = [2, "desc"]
        context['actividad'] = True
        ver_kwargs = self.kwargs.copy()
        ver_kwargs['actividad_id'] = 7495261  # pasamos inicialmente un id aleatorio
        context['datatable_row_link'] = reverse('actividad_ver', kwargs=ver_kwargs)
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
    columns = ['id', 'nombre', 'fechaHora', 'responsable']
    order_columns = ['', '', 'fechaHora', '']
    max_display_length = 100

    def get_initial_queryset(self):
        return Actividad.objects.filter(usSprint=self.usp)

    def render_column(self, row, column):
        if column == 'fechaHora':
            return row.fechaHora.astimezone().strftime("%d/%m/%Y %H:%M:%S")
        else:
            return super().render_column(row, column)


class ActividadPerfilView(ActividadBaseView, PermisosEsMiembroMixin, DetailView):
    """
    Vista para ver una actividad
    """
    model = Actividad
    context_object_name = 'actividad'
    template_name = 'proyecto/actividad/actividad_perfil.html'
    pk_url_kwarg = 'actividad_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Ver Actividad'
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.proyecto.id,))},
            {'nombre': 'Sprint %d' % self.sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': self.usp.us.nombre, 'url': reverse('sprint_us_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': 'Actividades', 'url': reverse('actividad_list', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': self.actividad.nombre, 'url': '#'},
        ]
        context['puedeEditar'] = self.usp.asignee.miembro.user == self.request.user
        return context


class ActividadUpdateView(SuccessMessageMixin, ActividadBaseView, PermissionRequiredMixin, UpdateView):
    """
    Vista para editar una actividad
    """
    model = Actividad
    form_class = ActividadForm
    template_name = 'change_form.html'
    pk_url_kwarg = 'actividad_id'

    def has_permission(self):
        return self.usp.asignee.miembro.user == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Actividad editada exitosamente"

    def get_success_url(self):
        return reverse('actividad_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id, self.actividad.id))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'usp': self.usp,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar la Actividad'
        context['titulo_form_editar'] = 'Actividad'
        context['titulo_form_editar_nombre'] = self.get_object().nombre
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.proyecto.id,))},
            {'nombre': 'Sprint %d' % self.sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': self.usp.us.nombre, 'url': reverse('sprint_us_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': 'Actividades', 'url': reverse('actividad_list', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': self.actividad.nombre, 'url': reverse('actividad_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id, self.actividad.id))},
            {'nombre': 'Editar', 'url': '#'},
        ]

        return context
