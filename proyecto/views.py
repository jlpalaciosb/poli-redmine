from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse

from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.views.generic.base import ContextMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic.edit import FormView
from django_datatables_view.base_datatable_view import BaseDatatableView
from datetime import datetime

from proyecto.forms import ProyectoForm,RolProyectoForm, MiembroProyectoForm
from proyecto.models import Proyecto,RolProyecto


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
                # Si se ordena por el periodo la lista de resultados
                return qs.order_by(*['proyecto__nombre'])
            elif order == ['-proyecto']:
                return qs.order_by(*['-proyecto__nombre'])
            return qs.order_by(*order)
        return qs

    def filter_queryset(self, qs):
        """ Si search['value'] es proveido entonces filtramos todas las columnas usando icontains
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


class ProyectoListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'proyecto/proyecto/change_list.html'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ProyectoListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Proyectos'
        context['crear_button'] = True
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


class ProyectoListJson(LoginRequiredMixin, PermissionRequiredMixin, CustomFilterBaseDatatableView):
    model = Proyecto
    columns = ['id', 'nombre', 'fechaInicioEstimada', 'fechaInicioEstimada', 'estado']
    order_columns = ['id', 'nombre', 'fechaInicioEstimada', 'fechaInicioEstimada', 'estado']
    max_display_length = 100
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'


class ProyectoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
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

    def form_valid(self, form):
        proyecto = form.save(commit=False)
        if not form.instance.pk:
            proyecto.usuario_creador_id = self.request.user.id
            proyecto.usuario_modificador_id = self.request.user.id
        else:
            proyecto.usuario_modificador_id = self.request.user.id

        return super().form_valid(form)




class ProyectoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
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
        context['titulo'] = 'Proyecto'
        context['titulo_form_editar'] = 'Datos del Proyecto'
        context['titulo_form_editar_nombre'] = context[ProyectoUpdateView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': context['proyecto'].nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Editar', 'url': '#'},
                                 ]

        return context

    def form_valid(self, form):
        proyecto = form.save(commit=False)
        if not form.instance.pk:
            proyecto.usuario_creador_id = self.request.user.id
            proyecto.usuario_modificador_id = self.request.user.id
        else:
            proyecto.usuario_modificador_id = self.request.user.id

        return super().form_valid(form)


class ProyectoPerfilView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Proyecto
    context_object_name = 'proyecto'
    template_name = 'proyecto/proyecto/change_list_perfil.html'
    pk_url_kwarg = 'proyecto_id'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ProyectoPerfilView, self).get_context_data(**kwargs)
        context['titulo'] = 'Perfil de Ṕroyecto'

        # context['crear_buttom'] = True
        # context['crear_ingreso_url'] = reverse('crear_ingreso', args=(context['contribuyente'].id, ))
        # context['crear_egreso_url'] = reverse('crear_egreso', args=(context['contribuyente'].id,))
        #
        # context['crear_ingreso_text_buttom'] = 'Nuevo Ingreso'
        # context['crear_egreso_text_buttom'] = 'Nuevo Egreso'
        #
        # # prestamos
        # context['lista_prestamos_buttom'] = 'Préstamos'
        # context['lista_prestamos_url'] = reverse('prestamos', args=(context['contribuyente'].id,))
        #
        # # resultados
        # context['lista_resultados_buttom'] = 'Resultados'
        # context['lista_resultados_url'] = reverse('resultados', args=(context['contribuyente'].id,))
        #
        # context['ingresos_text_tab'] = 'Ingresos'
        # context['egregsos_text_tab'] = 'Egresos'
        #
        # # importar url
        # context['importar_ingresos_url'] = reverse('importar_ingresos', args=(context['contribuyente'].id,))
        # context['importar_egresos_url'] = reverse('importar_egresos', args=(context['contribuyente'].id,))
        # context['pdf_generate_formulario104v3_url'] = reverse('pdf_generate_formulario104v3', args=(context['contribuyente'].id,))
        #
        # # Error importacion
        # error_importacion = self.request.session['error_importacion'] if 'error_importacion' in self.request.session else None
        #
        # if error_importacion:
        #     del self.request.session['error_importacion']
        #     context['error_importacion_exists'] = error_importacion
        #
        # # datatables
        # tipo = self.request.GET.get('tipo', None)  # tipo ingreso o egreso
        # if tipo:
        #     if tipo == 'ingreso':
        #         context['nombres_columnas'] = ['id', 'Fecha', 'Tipo de Documento', 'Operación',
        #                                        'Ingreso Gravado', 'Ingreso No Gravado']
        #         context['order'] = [1, "asc"]
        #         context['datatable_row_link'] = reverse('editar_ingreso', args=(
        #             context['contribuyente'].id, 1))  # pasamos inicialmente el id 1
        #         context['list_json'] = reverse('ingreso_list_json', args=(context['contribuyente'].id,))
        #
        #     elif tipo == 'egreso':
        #         context['nombres_columnas'] = ['id', 'Fecha', 'Tipo de Documento', 'Operación', 'Egreso Total']
        #         context['order'] = [1, "asc"]
        #         context['datatable_row_link'] = reverse('editar_egreso', args=(
        #             context['contribuyente'].id, 1))  # pasamos inicialmente el id 1
        #         context['list_json'] = reverse('egreso_list_json', args=(context['contribuyente'].id,))
        # else:
        #     context['nombres_columnas'] = ['id', 'Fecha', 'Tipo de Documento', 'Operación',
        #                                    'Ingreso Gravado', 'Ingreso No Gravado']
        #     context['order'] = [1, "asc"]
        #     context['datatable_row_link'] = reverse('editar_ingreso', args=(
        #         context['contribuyente'].id, 1))  # pasamos inicialmente el id 1
        #     context['list_json'] = reverse('ingreso_list_json', args=(context['contribuyente'].id, ))

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': context['proyecto'].nombre,'url': '#'}
                                 ]

        return context

class RolListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(RolListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Lista de Roles del Proyecto '+ proyecto.nombre
        context['crear_button'] = True
        context['crear_url'] = reverse('proyecto_rol_crear',kwargs=self.kwargs)
        context['crear_button_text'] = 'Nuevo Rol del Proyecto'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('proyecto_rol_editar', args=(self.kwargs['proyecto_id'],99999))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('proyecto_rol_list_json', kwargs=self.kwargs)
        context['roles']=True
        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Proyectos', 'url': reverse('proyectos')},
                    {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                    {'nombre': 'Roles', 'url': '#'}
                   ]



        return context


class RolListJson(LoginRequiredMixin, PermissionRequiredMixin, CustomFilterBaseDatatableView):
    model = RolProyecto
    columns = ['id', 'nombre']
    order_columns = ['id', 'nombre']
    max_display_length = 100
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def get_initial_queryset(self):
        """
        Se sobreescribe el metodo para que la lista sean todos los roles de un proyecto en particular
        :return:
        """
        proyecto=Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        return proyecto.rolproyecto_set.all()

class RolProyectoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = RolProyecto
    template_name = "change_form.html"
    form_class = RolProyectoForm
    permission_required = 'proyecto.add_proyecto'
    permission_denied_message = 'No tiene permiso para Crear nuevos proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Rol de Proyecto '{}' creado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('proyecto_rol_list',kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(RolProyectoCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_rol_list',kwargs=self.kwargs),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RolProyectoCreateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Roles de Proyectos'
        context['titulo_form_crear'] = 'Insertar Datos del Rol del Proyecto'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Roles', 'url': reverse('proyecto_rol_list',kwargs=self.kwargs)},
                                 {'nombre': 'Crear', 'url': '#'}
                                 ]

        return context

    def form_valid(self, form):
        rol = form.save(commit=False)
        if not form.instance.pk:
            rol.proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        rol.name = rol.nombre+rol.proyecto.id.__str__()
        print(rol.name)
        print(rol.nombre)

        return super().form_valid(form)

class RolProyectoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = RolProyecto
    form_class = RolProyectoForm
    context_object_name = 'rol'
    template_name = 'change_form.html'
    pk_url_kwarg = 'rol_id'
    permission_required = 'proyecto.change_proyecto'
    permission_denied_message = 'No tiene permiso para Editar Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Rol de Proyecto '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('proyecto_rol_list', args=(self.kwargs['proyecto_id'],))

    def get_form_kwargs(self):
        kwargs = super(RolProyectoUpdateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RolProyectoUpdateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Roles de Proyectos'
        context['titulo_form_crear'] = 'Insertar Datos del Rol del Proyecto'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Roles', 'url': reverse('proyecto_rol_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Editar', 'url': '#'}
                                 ]

        return context

    def form_valid(self, form):
        rol = form.save(commit=False)
        if not form.instance.pk:
            rol.proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        rol.name = rol.nombre + rol.proyecto.id.__str__()
        print(rol.name)
        print(rol.nombre)

        return super().form_valid(form)

class MiembroProyectoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = RolProyecto
    template_name = "change_form.html"
    form_class = MiembroProyectoForm
    permission_required = 'proyecto.add_proyecto'
    permission_denied_message = 'No tiene permiso para Crear nuevos proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Miembro de Proyecto '{}' creado exitosamente.".format(cleaned_data['user'])

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
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Miembro de Proyectos'
        context['titulo_form_crear'] = 'Insertar Datos del Miembro del Proyecto'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list',kwargs=self.kwargs)},
                                 {'nombre': 'Crear', 'url': '#'}
                                 ]

        return context

class MiembroProyectoListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(MiembroProyectoListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Lista de Miembros del Proyecto '+ proyecto.nombre
        context['crear_button'] = True
        context['crear_url'] = reverse('proyecto_miembro_crear',kwargs=self.kwargs)
        context['crear_button_text'] = 'Nuevo Miembro del Proyecto'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre del Miembro']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = '#'#reverse('proyecto_rol_editar', args=(self.kwargs['proyecto_id'],99999))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('proyecto_miembro_list_json', kwargs=self.kwargs)
        context['roles']=True
        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Proyectos', 'url': reverse('proyectos')},
                    {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                    {'nombre': 'Miembros', 'url': '#'}
                   ]



        return context


class MiembroProyectoListJson(LoginRequiredMixin, PermissionRequiredMixin, CustomFilterBaseDatatableView):
    model = RolProyecto
    columns = ['id', 'user']
    order_columns = ['id', 'user']
    max_display_length = 100
    permission_required = 'proyecto.view_proyecto'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def get_initial_queryset(self):
        """
        Se sobreescribe el metodo para que la lista sean todos los roles de un proyecto en particular
        :return:
        """
        proyecto=Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        return proyecto.miembroproyecto_set.all()
