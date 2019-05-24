from django.views.generic import TemplateView, DetailView, UpdateView, CreateView

from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.mixins import LoginRequiredMixin
from proyecto.forms import USForm, USCancelarForm
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoEnEjecucionMixin, UserStoryNoModificable
from proyecto.models import MiembroProyecto, Proyecto, UserStory


class USCreateView(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, CreateView):
    """
    Vista para crear un US para el proyecto
    """
    model = UserStory
    template_name = 'proyecto/us/us_change_form.html'
    form_class = USForm
    permission_required = 'proyecto.add_us'

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se crea correctamente

        :param cleaned_data:
        :return:
        """
        return "US creado exitosamente"

    def get_success_url(self):
        """
        El sitio donde se redirige al crear correctamente

        :return:
        """
        return reverse('proyecto_us_list', kwargs=self.kwargs)

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de creacion

        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_us_list', kwargs=self.kwargs),
            'proyecto_id': self.kwargs['proyecto_id'],
            'creando': True,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])

        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear US'
        context['titulo_form_crear'] = 'Insertar Datos del US'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
            {'nombre': 'Product Backlog', 'url': reverse('proyecto_us_list', kwargs=self.kwargs)},
            {'nombre': 'Crear US', 'url': '#'}
        ]

        context['proyecto_id'] = p.id

        return context


class USListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para ver el product backlog del proyecto
    """
    template_name = 'proyecto/us/us_list.html'
    estado = '*' # estado de los USs a listar (* significa todos los estados)

    def dispatch(self, request, *args, **kwargs):
        self.estado = request.GET.get('estado', '*')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])

        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Product Backlog'
        context['crear_button'] = self.request.user.has_perm('proyecto.add_us', p)
        context['crear_url'] = reverse('proyecto_us_crear', kwargs=self.kwargs)
        context['crear_button_text'] = 'Crear US'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre', 'Priorización', 'Estado General', 'Comentarios Adicionales']
        context['order'] = [2, "desc"]
        ver_kwargs = self.kwargs.copy()
        ver_kwargs['us_id'] = 7836271  # pasamos inicialmente un id aleatorio
        context['datatable_row_link'] = reverse('proyecto_us_ver', kwargs=ver_kwargs)
        context['list_json'] = reverse('proyecto_us_list_json', kwargs=kwargs) + '?estado=' + self.estado
        context['user_story'] = True
        context['selected'] = self.estado

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', kwargs=kwargs)},
            {'nombre': 'Product Backlog', 'url': '#'},
        ]

        return context


class USListJsonView(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista que retorna en json la lista de user stories del product backlog
    """
    model = MiembroProyecto
    columns = ['id', 'nombre', 'priorizacion', 'estadoProyecto','comentarios']
    order_columns = ['id', 'nombre', 'priorizacion', 'estadoProyecto']
    max_display_length = 100

    def get_initial_queryset(self):
        """
        Se obtiene una lista de los elementos correspondientes

        :return:
        """
        iqs = Proyecto.objects.get(pk=self.kwargs['proyecto_id']).userstory_set.all()
        st = self.request.GET.get('estado', '*')
        if st == '1' or st == '2' or st == '3' or st == '4' or st == '5' or st == '6':
            iqs = iqs.filter(estadoProyecto=int(st))
        return iqs

    def render_column(self, row, column):
        if column == 'priorizacion':
            return "{0:.2f}".format(row.get_priorizacion())
        if column == 'comentarios':
            #SI EL US NO TERMINO EN UN SPRINT Y SU TIEMPO PLANIFICADO EXCEDE AL TIEMPO EJECUTADO ENTONCES ADVERTIR AL USUARIO
            if row.tiene_tiempo_excedido() and row.estadoProyecto==3:
                return 'Falta ajustar las horas planificadas'
            else:
                return ''
        else:
            return super().render_column(row, column)

    def filter_queryset(self, qs):
        search = self._querydict.get('search[value]', '')
        return qs.filter(nombre__icontains=search)


class USPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
    Vista para ver los datos básicos de un User Story a nivel de proyecto
    """
    model = UserStory
    context_object_name = 'us'
    template_name = 'proyecto/us/us_perfil.html'
    pk_url_kwarg = 'us_id'

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)

        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        us = context['object']

        context['titulo'] = 'User Story'

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


class USUpdateView(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, UserStoryNoModificable, UpdateView):
    """
    Vista que permite modificar los datos básicos de un User Story a nivel proyecto
    """
    model = UserStory
    form_class = USForm
    template_name = 'proyecto/us/us_change_form.html'
    pk_url_kwarg = 'us_id'
    permission_required = 'proyecto.change_us'

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se edita correctamente

        :param cleaned_data:
        :return:
        """
        return "US editado exitosamente"

    def get_success_url(self):
        """
        El sitio donde se redirige al modificar correctamente

        :return:
        """
        pid = self.kwargs['proyecto_id']
        uid = self.kwargs['us_id']
        return reverse('proyecto_us_ver', args=(pid, uid))

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion

        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
            'creando': False,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
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

        context['proyecto_id'] = p.id

        return context


class USCancelarView(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin, UpdateView):
        """
        Vista que permite cancelar un User Story a nivel proyecto
        """
        model = UserStory
        context_object_name = 'us'
        form_class = USCancelarForm
        template_name = 'proyecto/us/us_cancelar.html'
        pk_url_kwarg = 'us_id'
        permission_required = 'proyecto.change_us'
        proyecto = None # el proyecto en cuestión
        us = None # el user story en cuestión

        def dispatch(self, request, *args, **kwargs):
            self.proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
            self.us = UserStory.objects.get(pk=kwargs['us_id'])
            cancelable = self.cancelable()
            if cancelable != 'yes':
                messages.add_message(
                    request, messages.WARNING, 'No se puede cancelar el user story porque %s' % cancelable
                )
                return HttpResponseRedirect(self.get_success_url())
            return super().dispatch(request, *args, **kwargs)

        def get_success_message(self, cleaned_data):
            """
            El mensaje que aparece cuando se cancela correctamente

            :param cleaned_data:
            :return:
            """
            return "User Story cancelado"

        def get_success_url(self):
            """
            El sitio donde se redirige al cancelar correctamente

            :return:
            """
            return reverse('proyecto_us_ver', args=(self.proyecto.id, self.us.id))

        def get_context_data(self, **kwargs):
            """
            Las variables de contexto del template

            :param kwargs:
            :return:
            """
            context = super().get_context_data(**kwargs)
            context['titulo'] = 'Cancelar User Story'
            context['breadcrumb'] = [
                {'nombre': 'Inicio', 'url': '/'},
                {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                {'nombre': self.proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.proyecto.id,))},
                {'nombre': 'Product Backlog', 'url': reverse('proyecto_us_list', args=(self.proyecto.id,))},
                {'nombre': self.us.nombre, 'url': reverse('proyecto_us_ver', args=(self.proyecto.id, self.us.id))},
                {'nombre': 'Cancelar', 'url': '#'}
            ]
            return context

        # retorna 'yes' o el motivo de por qué no se puede cancelar
        def cancelable(self):
            """
            Controla si se puede cancelar el user story

            ``return:``
                retorna 'yes' o el motivo de por qué no se puede cancelar
            """
            if self.proyecto.estado != 'EN EJECUCION':
                return 'el proyecto debe estar en ejecución'
            elif self.us.estadoProyecto not in [1, 3]:
                return 'el user story debe estar pendiente o no terminado'
            else:
                return 'yes'
