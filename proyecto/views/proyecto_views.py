from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden
from guardian.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import  PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from proyecto.forms import ProyectoForm
from proyecto.models import Proyecto, MiembroProyecto
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
        return "Proyecto '{}' creado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('proyectos')

    def get_form_kwargs(self):
        kwargs = super(ProyectoCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyectos'),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProyectoCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Proyectos'
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
        return "Proyecto '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('perfil_proyecto', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(ProyectoUpdateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
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
        context = super(ProyectoPerfilView, self).get_context_data(**kwargs)
        context['titulo'] = 'Perfil del Proyecto'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': context['proyecto'].nombre,'url': '#'}
                                 ]

        return context
