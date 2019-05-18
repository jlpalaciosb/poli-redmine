from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib import messages

from proyecto.forms import ActividadForm
from proyecto.mixins import PermisosEsMiembroMixin
from proyecto.models import Proyecto, Sprint, UserStorySprint, Actividad


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

    **Condiciones:**

    - Solo el encargado del user story podra acceder a esta vista
    - Solo cuando el sprint asociado este en ejecucion se podra acceder a esta vista
    - Solo cuando el user story este en DOING se podra acceder a esta vista
    """
    model = Actividad
    template_name = "change_form.html"
    form_class = ActividadForm
    redirect = False # si en principio el usuario tiene permiso para agregar una actividad pero no puede por las restricciones del sistema

    def has_permission(self):
        """
        Se controla que el permiso sea de acuerdo al encargado del user story
        :return:
        """
        parcial = self.usp.asignee.miembro.user == self.request.user
        if parcial:
            if self.usp.sprint.estado != 'EN_EJECUCION':
                messages.add_message(self.request, messages.WARNING, 'El sprint debe estar en ejecución')
                self.redirect = True
            elif self.usp.estado_fase_sprint != 'DOING':
                messages.add_message(self.request, messages.WARNING, 'Es user story debe estar en la etapa DOING')
                self.redirect = True
            return self.redirect == False
        else:
            return False

    def handle_no_permission(self):
        """
        En caso de que no tenga permiso se tira 403.
        :return:
        """
        if self.redirect:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se crea correctamente

        :param cleaned_data:
        :return:
        """
        return "Actividad agregada exitosamente"

    def get_success_url(self):
        """
        El sitio donde se redirige al crear correctamente
        :return:
        """
        return reverse('actividad_list', kwargs=self.kwargs)

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de creacion
        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': reverse('actividad_list', kwargs=self.kwargs),
            'usp': self.usp,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
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
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)

        context['titulo'] = 'Actividades del User Story'

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
        """
        Se obtiene una lista de los elementos correspondientes
        :return:
        """
        return Actividad.objects.filter(usSprint__us=self.usp.us, usSprint__sprint__orden__lte=self.usp.sprint.orden)

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

    def dispatch(self, request, *args, **kwargs):
        incons = self.inconsistente()
        if incons:
            return incons
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
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
        context['puedeEditar'] = self.usp.asignee.miembro.user == self.request.user and self.usp.sprint.estado == 'EN_EJECUCION'
        return context

    def inconsistente(self):
        actividad = self.get_object()
        actividad_proyecto_id = str(actividad.usSprint.sprint.proyecto.id)
        actividad_sprint_id = str(actividad.usSprint.sprint.id)
        actividad_usp_id = str(actividad.usSprint.id)
        if actividad_proyecto_id != self.kwargs['proyecto_id'] or \
           actividad_sprint_id != self.kwargs['sprint_id'] or \
           actividad_usp_id != self.kwargs['usp_id']:
            return HttpResponseRedirect(reverse('actividad_ver',
                args=(actividad_proyecto_id, actividad_sprint_id, actividad_usp_id, actividad.id)))


class ActividadUpdateView(SuccessMessageMixin, ActividadBaseView, PermissionRequiredMixin, UpdateView):
    """
    Vista para editar una actividad

     **Condiciones:**

    - Solo el encargado del user story podra acceder a esta vista
    - Solo cuando el sprint asociado este en ejecucion se podra acceder a esta vista
    - Si el user story se encuentra terminado no se podra acceder a este vista
    """
    model = Actividad
    form_class = ActividadForm
    template_name = 'change_form.html'
    pk_url_kwarg = 'actividad_id'
    redirect = False # si en principio el usuario tiene permiso para agregar una actividad pero no puede por las restricciones del sistema

    def has_permission(self):
        parcial = self.usp.asignee.miembro.user == self.request.user
        if parcial:
            if self.usp.sprint.estado != 'EN_EJECUCION':
                messages.add_message(self.request, messages.WARNING, 'El sprint debe estar en ejecución')
                self.redirect = True
            elif self.usp.fase_sprint.es_ultima_fase() and self.usp.estado_fase_sprint == 'DONE':
                messages.add_message(self.request, messages.WARNING, 'No se puede modificar la actividad de un user story cuando el user story esta DONE en la última fase')
                self.redirect = True
            return self.redirect == False
        else:
            return False

    def handle_no_permission(self):
        if self.redirect:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se edita correctamente

        :param cleaned_data:
        :return:
        """
        return "Actividad editada exitosamente"

    def get_success_url(self):
        """
        El sitio donde se redirige al editar correctamente
        :return:
        """
        return reverse('actividad_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id, self.actividad.id))

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion
        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'usp': self.usp,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
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
