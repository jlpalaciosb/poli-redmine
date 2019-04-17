from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden, Http404

from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from proyecto.forms import ProyectoForm,RolProyectoForm, MiembroProyectoForm,EditarMiembroForm
from proyecto.mixins import GuardianAnyPermissionRequiredMixin, ProyectoMixin
from proyecto.models import Proyecto,RolProyecto,MiembroProyecto
from ProyectoIS2_9.utils import cualquier_permiso


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
    """
    Vista Basada en Clases para listar los proyectos existentes
    """

    template_name = 'proyecto/proyecto/change_list.html'
    permission_required = ('proyecto.add_proyecto', 'proyecto.change_proyecto', 'proyecto.delete_proyecto')
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())

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


class ProyectoListJson(LoginRequiredMixin, PermissionRequiredMixin, CustomFilterBaseDatatableView):
    model = Proyecto
    columns = ['id', 'nombre', 'fechaInicioEstimada', 'fechaInicioEstimada','estado']
    order_columns = ['id', 'nombre', 'fechaInicioEstimada', 'fechaInicioEstimada', 'estado']
    max_display_length = 100
    permission_required = ('proyecto.add_proyecto', 'proyecto.change_proyecto', 'proyecto.delete_proyecto')
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())


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




class ProyectoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
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



class ProyectoPerfilView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
           Vista Basada en Clases para la visualizacion del perfil de un proyecto
    """
    model = Proyecto
    context_object_name = 'proyecto'
    template_name = 'proyecto/proyecto/change_list_perfil.html'
    pk_url_kwarg = 'proyecto_id'
    permission_required = ('proyecto.add_proyecto', 'proyecto.change_proyecto', 'proyecto.delete_proyecto')
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())

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

class RolListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'change_list.html'
    permission_required = 'proyecto.change_proyecto'
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
    permission_required = 'proyecto.change_proyecto'
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
    permission_required = 'proyecto.change_proyecto'
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
            'proyecto_id': self.kwargs['proyecto_id'],
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
            'proyecto_id': self.kwargs['proyecto_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RolProyectoUpdateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Editar Rol de Proyecto'
        context['titulo_form_editar'] = 'Datos del Rol'
        context['titulo_form_editar_nombre'] = context[RolProyectoUpdateView.context_object_name].nombre

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
        rol.name = rol.nombre + rol.proyecto.id.__str__()
        print(rol.name)
        print(rol.nombre)

        return super().form_valid(form)


class MiembroProyectoCreateView(LoginRequiredMixin, GuardianPermissionRequiredMixin, SuccessMessageMixin,
                                CreateView, ProyectoMixin):
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
        context['nombres_columnas'] = ['id', 'Nombre de Usuario']
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
                              CustomFilterBaseDatatableView, ProyectoMixin):
    model = MiembroProyecto
    columns = ['id', 'user.username']
    order_columns = ['id', 'user.username']
    permission_required = (
        'proyecto.add_miembroproyecto',
        'proyecto.change_miembroproyecto',
        'proyecto.delete_miembroproyecto',
    ) # Tiene permiso al tener cualquiera de estos permisos
    return_403 = True
    permission_denied_message = 'No tiene permiso para ver la lista de miembros de este proyecto'

    def get_permission_object(self): return self.get_proyecto()

    def get_initial_queryset(self):
        return self.get_proyecto().miembroproyecto_set.all()


class MiembroProyectoPerfilView(LoginRequiredMixin, GuardianAnyPermissionRequiredMixin, DetailView,
                                ProyectoMixin):
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

