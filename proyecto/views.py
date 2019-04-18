from django.db.models.query_utils import Q
from django.http import HttpResponseForbidden

from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponseRedirect

from proyecto.forms import ProyectoForm,RolProyectoForm, MiembroProyectoForm,EditarMiembroForm
from proyecto.mixins import GuardianAnyPermissionRequiredMixin
from proyecto.models import Proyecto,RolProyecto,MiembroProyecto
from ProyectoIS2_9.utils import cualquier_permiso
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin
from guardian.shortcuts import get_perms


class PermisosPorProyecto(GuardianPermissionRequiredMixin):
    """
    Clase a ser heredada por las vistas que necesitan autorizacion de permisos para un proyecto en particular. Se debe especificar la lista de permisos
    """
    return_403 = True
    proyecto_param = 'proyecto_id'#El parametro que contiene el id del proyecto a verificar

    def get_permission_object(self):
        """
        Metodo que obtiene el proyecto con el cual los permisos a verificar deberian estar asociados
        :return:
        """
        return Proyecto.objects.get(pk=self.kwargs[self.proyecto_param])

class PermisosEsMiembro(PermissionRequiredMixin):
    """
    Clase a ser heredada por las vistas de un proyecto que necesitan comprobar si un usuario es miembro de un proyecto para permitir acceso a las mismas.
    Es decir, si es miembro del proyecto podra acceder a la vista. Usada gralmente para vistas que involucran solo visualizacion
    """
    proyecto_param = 'proyecto_id'  # El parametro que contiene el id del proyecto a verificar

    def has_permission(self):
        """
        Si el usuario que hace el request es miembro del proyecto por quien solicita entonces tiene permisos
        :return: True si el usuario es miembro y false si el usuario no es miembro del proyecto
        """
        try:
            MiembroProyecto.objects.get(user=self.request.user,proyecto__pk=self.kwargs[self.proyecto_param])
            return True
        except MiembroProyecto.DoesNotExist:
            return False

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

class RolListView(LoginRequiredMixin, PermisosEsMiembro, TemplateView):
    """
    Vista para listar roles de proyecto de un proyecto en especifico.
    """
    template_name = 'change_list.html'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(RolListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Lista de Roles del Proyecto '+ proyecto.nombre
        context['crear_button'] = 'add_rolproyecto' in get_perms(self.request.user, proyecto)
        context['crear_url'] = reverse('proyecto_rol_crear',kwargs=self.kwargs)
        context['crear_button_text'] = 'Nuevo Rol del Proyecto'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('proyecto_rol_ver', args=(self.kwargs['proyecto_id'],99999))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('proyecto_rol_list_json', kwargs=self.kwargs)
        context['roles']=True
        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Proyectos', 'url': reverse('proyectos')},
                    {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                    {'nombre': 'Roles', 'url': '#'}
                   ]



        return context


class RolListJson(LoginRequiredMixin, PermisosEsMiembro, CustomFilterBaseDatatableView):
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

class RolProyectoCreateView(LoginRequiredMixin, PermisosPorProyecto, SuccessMessageMixin, CreateView):
    """
    Vista para creacion de un rol de proyecto. Se crean roles que no sean por defecto
    """
    model = RolProyecto
    template_name = "change_form.html"
    form_class = RolProyectoForm
    permission_required = 'proyecto.add_rolproyecto'
    permission_denied_message = 'No tiene permiso para Crear nuevos roles de proyecto.'

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

class RolProyectoUpdateView(LoginRequiredMixin, PermisosPorProyecto, SuccessMessageMixin, UpdateView):
    """
    Vista para edicion de un rol de proyecto. No funciona para roles de proyecto que sean por defecto
    """
    model = RolProyecto
    form_class = RolProyectoForm
    context_object_name = 'rol'
    template_name = 'change_form.html'
    pk_url_kwarg = 'rol_id'
    permission_required = 'proyecto.change_rolproyecto'
    permission_denied_message = 'No tiene permiso para Editar Roles del Proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def check_permissions(self, request):
        """
        Se sobreescribe el metodo para evitar que los roles que sean por defecto no puedan ser editados
        :param request:
        :return:
        """
        try:
            rol = RolProyecto.objects.get(pk=self.kwargs['rol_id'])
            if rol.is_default:
               return self.handle_no_permission()
        finally:
            super(RolProyectoUpdateView, self).check_permissions(request)



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
                                 {'nombre': 'Ver', 'url': reverse('proyecto_rol_ver', args=(self.kwargs['proyecto_id'],self.kwargs['rol_id']))},
                                 {'nombre': 'Editar', 'url': '#'}
                                 ]

        return context

    def form_valid(self, form):
        rol = form.save(commit=False)
        rol.name = rol.nombre + rol.proyecto.id.__str__()
        print(rol.name)
        print(rol.nombre)

        return super().form_valid(form)


class RolPerfilView(LoginRequiredMixin, PermisosEsMiembro, DetailView):
    """
           Vista Basada en Clases para la visualizacion del perfil de un rol de proyecto
    """
    model = RolProyecto
    context_object_name = 'rol'
    template_name = 'proyecto/rolproyecto/rolproyecto_perfil.html'
    pk_url_kwarg = 'rol_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(RolPerfilView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Ver Rol de Proyecto'
        context['titulo_form_editar'] = 'Datos del Rol'
        context['titulo_form_editar_nombre'] = context[RolPerfilView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Roles',
                                  'url': reverse('proyecto_rol_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': context[self.context_object_name].nombre, 'url': '#'}
                                 ]

        return context

class RolEliminarView(LoginRequiredMixin, PermisosPorProyecto,SuccessMessageMixin, DeleteView):
    """
    Vista que elimina un rol de proyecto en caso que tenga los permisos necesarios, no sea un rol de proyecto predeterminado ni este asociado con algun miembro
    """
    model = RolProyecto
    context_object_name = 'rol'
    template_name = 'proyecto/rolproyecto/rolproyecto_eliminar.html'
    pk_url_kwarg = 'rol_id'
    permission_required = 'proyecto.delete_rolproyecto'
    permission_denied_message = 'No tiene permiso para eliminar el rol.'
    success_message = 'Rol eliminado correctamente'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_url(self):
        return reverse('proyecto_rol_list', args=(self.kwargs['proyecto_id'],))

    def check_permissions(self, request):
        """
        Se sobreescribe el metodo para evitar que los roles que sean por defecto no puedan ser eliminados
        :param request:
        :return:
        """
        try:
            rol = RolProyecto.objects.get(pk=self.kwargs['rol_id'])
            if rol.is_default:
               return self.handle_no_permission()
        finally:
            super(RolEliminarView, self).check_permissions(request)

    def get_success_message(self, cleaned_data):
        return "Rol eliminado exitosamente."

    def get_context_data(self, **kwargs):
        context = super(RolEliminarView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Eliminar Rol'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Roles', 'url': reverse('proyecto_rol_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': context[self.context_object_name].nombre, 'url': reverse('proyecto_rol_ver', args=(self.kwargs['proyecto_id'],self.kwargs['rol_id']))},
            {'nombre': 'Eliminar', 'url': '#'}
        ]
        context['eliminable'] = self.eliminable()
        return context

    def eliminable(self):
        """
        Si un rol de proyecto esta asociado con un miembro de algun proyecto entonces no se puede eliminar.
        :return:
        """
        return not self.get_object().miembroproyecto_set.all()

    def post(self, request, *args, **kwargs):
        if self.eliminable():
            return super(RolEliminarView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.success_url)
