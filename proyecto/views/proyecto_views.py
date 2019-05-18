from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect
from guardian.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import  PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from ProyectoIS2_9.utils import cambiable_estado_proyecto
from proyecto.forms import ProyectoForm, ProyectoCambiarEstadoForm
from proyecto.models import Proyecto, MiembroProyecto,Actividad, UserStory
from proyecto.models import models
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin


class CustomFilterBaseDatatableView(BaseDatatableView):
    def ordering(self, qs):
        """
        Obtiene los parámteros del request y prepara el order by
        (Utlizado de la librería django-datatables-view)
        """

        # Number of columns that are used in sorting
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get('iSortingCols', 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = 'order[{0}][column]'.format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = 'order[{0}][column]'.format(sorting_cols)

        order = []
        order_columns = self.get_order_columns()

        for i in range(sorting_cols):
            # sorting column
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0

            sdir = '-' if sort_dir == 'desc' else ''
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

        if order:
            if order == ['proyecto']:
                return qs.order_by(*['proyecto__nombre'])
            elif order == ['-proyecto']:
                return qs.order_by(*['-proyecto__nombre'])
            return qs.order_by(*order)
        return qs

    def filter_queryset(self, qs):
        """
        Si search['value'] es proveido entonces filtramos todas las columnas usando icontains
        (Sobreescribimos el método proveído por la librería que utilizaba istartswith)
        """
        if not self.pre_camel_case_notation:
            # get global search value
            search = self._querydict.get('search[value]', None)
            col_data = self.extract_datatables_column_data()
            q = Q()
            for col_no, col in enumerate(col_data):
                # apply global search to all searchable columns
                if search and col['searchable']:
                    # Se agrega el filtro para los nombres de operacion y de categoria
                    if self.columns[col_no] != 'operacion' and self.columns[col_no] != 'categoria':
                        if self.columns[col_no] != 'proyecto':
                            q |= Q(**{'{0}__icontains'.format(self.columns[col_no].replace('.', '__')): search})
                        else:
                            q |= Q(**{'{0}__anho__icontains'.format(self.columns[col_no].replace('.', '__')): search})
                    else:
                        q |= Q(**{'{0}__nombre__icontains'.format(self.columns[col_no].replace('.', '__')): search})

                # column specific filter
                if col['search.value']:
                    qs = qs.filter(**{
                        '{0}__icontains'.format(self.columns[col_no].replace('.', '__')): col['search.value']})
            qs = qs.filter(q)
        return qs


class ProyectoListView(LoginRequiredMixin, TemplateView):
    """
    Vista Basada en Clases para listar los proyectos existentes
    """

    template_name = 'proyecto/proyecto/change_list.html'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(ProyectoListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Proyectos'
        context['crear_button'] = self.request.user.has_perm('proyecto.add_proyecto')
        context['crear_url'] = reverse('crear_proyecto')
        context['crear_button_text'] = 'Nuevo Proyecto'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre', 'Fecha de inicio', 'Fecha de Finalizacion',
                                       'Estado']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('perfil_proyecto', args=(1,))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('proyecto_list_json')

        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Proyectos', 'url': '#'},
                   ]



        return context


class ProyectoListJson(LoginRequiredMixin, CustomFilterBaseDatatableView, ):
    model = Proyecto
    columns = ['id', 'nombre', 'fechaInicioEstimada', 'fechaInicioEstimada','estado']
    order_columns = ['id', 'nombre', 'fechaInicioEstimada', 'fechaInicioEstimada', 'estado']
    max_display_length = 100

    def get_initial_queryset(self):
        """
        Un usuario es miembro de distintos proyectos. Se obtiene todos los proyectos con los que esta relacionados a traves de la lista de Miembro del user

        :return:
        """
        return Proyecto.objects.filter(id__in = list(map(lambda x: x.proyecto_id, MiembroProyecto.objects.filter(user=self.request.user))))


class ProyectoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vista Basada en Clases para la creacion de los proyectos
    """
    model = Proyecto
    template_name = "proyecto/proyecto/change_form.html"
    form_class = ProyectoForm
    permission_required = 'proyecto.add_proyecto'
    permission_denied_message = 'No tiene permiso para Crear nuevos proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se crea correctamente

        :param cleaned_data:
        :return:
        """
        return "Proyecto '{}' creado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        """
        El sitio donde se redirige al crear correctamente
        :return:
        """
        return reverse('proyectos')

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de creacion
        :return:
        """
        kwargs = super(ProyectoCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyectos'),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super(ProyectoCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Nuevo Proyecto'
        context['titulo_form_crear'] = 'Insertar Datos del Nuevo Proyecto'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': 'Crear', 'url': '#'}
                                 ]

        return context


class ProyectoUpdateView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, UpdateView):
    """
    Vista Basada en Clases para la actualizacion de los proyectos
    """
    model = Proyecto
    form_class = ProyectoForm
    context_object_name = 'proyecto'
    template_name = 'proyecto/proyecto/change_form.html'
    pk_url_kwarg = 'proyecto_id'
    permission_required = 'proyecto.change_proyecto'
    permission_denied_message = 'No tiene permiso para Editar Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se edita correctamente

        :param cleaned_data:
        :return:
        """
        return "Proyecto '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        """
        El sitio donde se redirige al editar correctamente
        :return:
        """
        return reverse('perfil_proyecto', kwargs=self.kwargs)

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion
        :return:
        """
        kwargs = super(ProyectoUpdateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super(ProyectoUpdateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Editar Proyecto'
        context['titulo_form_editar'] = 'Datos del Proyecto'
        context['titulo_form_editar_nombre'] = context[ProyectoUpdateView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': context['proyecto'].nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Editar', 'url': '#'},
                                 ]

        return context


class ProyectoPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
    Vista Basada en Clases para la visualizacion del perfil de un proyecto
    """
    model = Proyecto
    context_object_name = 'proyecto'
    template_name = 'proyecto/proyecto/change_list_perfil.html'
    pk_url_kwarg = 'proyecto_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super(ProyectoPerfilView, self).get_context_data(**kwargs)
        context['titulo'] = 'Perfil del Proyecto'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': context['proyecto'].nombre,'url': '#'}
                                 ]

        return context


class ProyectoCambiarEstadoView(LoginRequiredMixin, PermisosPorProyectoMixin, UpdateView):
    """
    Vista para cambiar el estado de un proyecto.

    **Diagrama de Estado:**

    .. image:: /media/diagrama_de_estado_proyecto.png

    **Condiciones:**

    - El usuario debe estar logueado.
    - El usuario debe tener el permiso change_proyecto sobre el proyecto.
    - Se debe cumplir las restricciones del diagrama de estado.
    - Para pasar a cancelado o suspendido o terminado, no debe tener ningún sprint en ejecución.
    - Para pasar a terminado no debe tener ningún user story pendiente o no terminado.
    """
    model = Proyecto
    proyecto = None # el proyecto en cuestión
    newst = None # el nuevo estado del proyecto
    form_class = ProyectoCambiarEstadoForm
    context_object_name = 'proyecto'
    template_name = 'proyecto/proyecto/cambiarestado.html'
    pk_url_kwarg = 'proyecto_id'
    permission_required = 'proyecto.change_proyecto'

    def dispatch(self, request, *args, **kwargs):
        self.proyecto = self.get_object()
        self.newst = request.GET.get('estado', '') # **
        camb = cambiable_estado_proyecto(self.proyecto, self.newst)
        if camb != 'yes':
            messages.add_message(request, messages.WARNING,
                'No se puede %s el proyecto porque %s' % (self.get_verbo(), camb))
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        El sitio donde se redirige al cambiar correctamente
        :return:
        """
        return reverse('perfil_proyecto', args=(self.proyecto.id,))

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context['titulo'] = '%s el Proyecto' % self.get_verbo().capitalize()
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': context['proyecto'].nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
            {'nombre': self.get_verbo().capitalize(), 'url': '#'},
        ]
        context['currentst'] = self.get_object().estado
        context['newst'] = self.newst
        context['verbo'] = self.get_verbo()
        return context

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion
        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({'estado': self.request.GET.get('estado', '')})
        return kwargs

    def form_valid(self, form):
        """
        Se controla la coherencia de los cambios de estado de un proyecto.
        :param form:
        :return:
        """
        messages.add_message(self.request, messages.SUCCESS, 'Ahora el proyecto está %s' % self.newst)
        return super().form_valid(form)

    def get_verbo(self):
        if self.newst == 'EN EJECUCION':
            return 'iniciar'
        elif self.newst == 'TERMINADO':
            return 'terminar'
        elif self.newst == 'CANCELADO':
            return 'cancelar'
        elif self.newst == 'SUSPENDIDO':
            return 'supender'
        else:
            return ''


class BurdownChartProyectoView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
    Vista Basada en Clases para la visualizacion del burdown chart de un proyecto
    """
    model = Proyecto
    context_object_name = 'proyecto'
    template_name = 'proyecto/proyecto/burdown_chart_proyecto.html'
    pk_url_kwarg = 'proyecto_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super(BurdownChartProyectoView, self).get_context_data(**kwargs)
        proyecto = context['proyecto']
        context['titulo'] = 'Burdown Chart del Proyecto {}'.format(proyecto.nombre)
        datos_grafica = Actividad.objects.filter(usSprint__sprint__proyecto_id=proyecto.id).values('usSprint__sprint__orden'
                                                                                         ).annotate(cantidad=models.Count('usSprint__sprint__orden'),total_por_sprint=models.Sum('horasTrabajadas'))
        total_a_trabajar=UserStory.objects.filter(proyecto=proyecto).aggregate(total_planificado=models.Sum('tiempoPlanificado'))['total_planificado']
        x_real = [0]
        y_real = [total_a_trabajar]



        acumulado = 0
        for dato in datos_grafica:
            x_real.append(dato['usSprint__sprint__orden'])
            acumulado = (acumulado + dato['total_por_sprint'])
            y_real.append(y_real[0] - acumulado)

        context['grafica'] = {'datos_en_x': x_real, 'datos_en_y': y_real}

        context['total'] = total_a_trabajar

        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': context['proyecto'].nombre,'url': reverse('perfil_proyecto',kwargs=self.kwargs)},
                                 {'nombre': 'Burdown Chart',
                                  'url': '#'}
                                 ]

        return context