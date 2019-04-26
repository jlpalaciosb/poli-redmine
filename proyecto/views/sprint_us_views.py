from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView
from django.http import HttpResponseForbidden
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from proyecto.forms import UserStorySprintCrearForm, UserStorySprintEditarForm
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin
from proyecto.models import Sprint, Proyecto, UserStorySprint


class UserStorySprintCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, CreateView):
    """
    Vista para agregar un user story a un sprint
    """
    model = UserStorySprint
    template_name = "change_form.html"
    form_class = UserStorySprintCrearForm
    permission_required = 'proyecto.administrar_sprint'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "User Story agregado exitosamente"

    def get_success_url(self):
        return reverse('sprint_us_list', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
            'sprint_id': self.kwargs['sprint_id'],
        })
        return kwargs

    def form_valid(self, form):
        # TODO : transaction

        # establecer estado del us seleccionado y su flujo
        us = form.cleaned_data['us']
        flujo = form.cleaned_data['flujo']
        us.estadoProyecto = 2
        if us.flujo is None:
            us.flujo = flujo
            us.fase = flujo.fase_set.get(orden=1)
            us.estadoFase = 'TODO'
        us.save()

        # calcular cantidad de horas disponibles en el sprint (recordar que sprint tiene un atributo llamado capacidad)
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        suma = 0 # cantidad de horas de trabajo por hacer
        for usp in UserStorySprint.objects.filter(sprint=sprint):
            restante = usp.us.tiempoPlanificado - usp.us.tiempoEjecutado
            suma += restante
        suma += us.tiempoPlanificado - us.tiempoEjecutado # sumar trabajo restante del US que se está agregando
        disponible = sprint.capacidad - suma
        if disponible > 0: messages.add_message(self.request, messages.INFO, 'Quedan ' + str(disponible) + ' horas disponibles en el sprint')
        else: messages.add_message(self.request, messages.WARNING, 'Capacidad del sprint superada por ' + str(-disponible) + ' horas')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar US al Sprint'
        context['titulo_form_crear'] = 'Datos'

        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Administrar Sprint', 'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
            {'nombre': 'User Stories', 'url': self.get_success_url()},
            {'nombre': 'Crear', 'url':'#'}
        ]

        return context


class UserStorySprintListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para ver el sprint backlog
    """
    template_name = 'change_list.html'

    def get_context_data(self, **kwargs):
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])

        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Sprint Backlog'
        context['crear_button'] = self.request.user.has_perm('proyecto.administrar_sprint', proyecto) and sprint.estado == 'PLANIFICADO'
        context['crear_url'] = reverse('sprint_us_agregar', kwargs=self.kwargs)
        context['crear_button_text'] = 'Agregar US'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre', 'Priorización']
        context['order'] = [2, "desc"]
        context['datatable_row_link'] = reverse('sprint_us_ver', args=(proyecto.id, sprint.id, 7483900))
        context['list_json'] = reverse('sprint_us_list_json', kwargs=kwargs)
        context['usp'] = True

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Administrar Sprint', 'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
            {'nombre': 'User Stories', 'url': '#'},
        ]

        return context


class UserStorySprintListJsonView(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista que retorna en json la lista de user stories del sprint backlog
    """
    model = UserStorySprint
    columns = ['id', 'us.nombre', 'us.priorizacion']
    order_columns = ['id', 'us.nombre', 'us.priorizacion']
    max_display_length = 100

    def get_initial_queryset(self):
        return UserStorySprint.objects.filter(sprint__id=self.kwargs['sprint_id'])

    def render_column(self, row, column):
        if column == 'us.priorizacion':
            return "{0:.2f}".format(row.us.priorizacion)
        else:
            return super().render_column(row, column)


class UserStorySprintPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
    Vista para ver los datos básicos de un User Story a nivel de sprint
    """
    model = UserStorySprint
    context_object_name = 'usp'
    template_name = 'proyecto/sprint/us/usp_perfil.html'
    pk_url_kwarg = 'usp_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        usp = context['object']

        context['titulo'] = 'Ver US en Sprint'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(proyecto.id,))},
            {'nombre': 'Administrar Sprint', 'url': reverse('proyecto_sprint_administrar', args=(proyecto.id, sprint.id))},
            {'nombre': 'User Stories', 'url': reverse('sprint_us_list', args=(proyecto.id, sprint.id))},
            {'nombre': usp.us.nombre, 'url': '#'},
        ]

        context['puedeEditar'] = self.request.user.has_perm('proyecto.administrar_sprint', proyecto) and sprint.estado == 'PLANIFICADO'

        return context


class UserStorySprintUpdateView(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin, UpdateView):
    """
    Vista que permite modificar un User Story a nivel proyecto (hasta ahora solo se permite cambiar el asignee)
    """
    model = UserStorySprint
    form_class = UserStorySprintEditarForm
    template_name = 'change_form.html'
    pk_url_kwarg = 'usp_id'
    permission_required = 'proyecto.administrar_sprint'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Se estableció el encargado exitosamente"

    def get_success_url(self):
        pid = self.kwargs['proyecto_id']
        sid = self.kwargs['sprint_id']
        uid = self.kwargs['usp_id']
        return reverse('sprint_us_ver', args=(pid, sid, uid))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
            'sprint_id': self.kwargs['sprint_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        usp = context['object']

        context['titulo'] = 'Cambiar Encargado del US en el Sprint'
        context['titulo_form_editar'] = 'US'
        context['titulo_form_editar_nombre'] = usp.us.nombre

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(proyecto.id,))},
            {'nombre': 'Administrar Sprint', 'url': reverse('proyecto_sprint_administrar', args=(proyecto.id, sprint.id))},
            {'nombre': 'User Stories', 'url': reverse('sprint_us_list', args=(proyecto.id, sprint.id))},
            {'nombre': usp.us.nombre, 'url': reverse('sprint_us_ver', args=(proyecto.id, sprint.id, usp.id))},
            {'nombre': 'Cambiar Encargado', 'url': '#'},
        ]

        return context
