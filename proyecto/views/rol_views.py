from django.http import HttpResponseForbidden

from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from guardian.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponseRedirect
from django.http import Http404
from proyecto.forms import RolProyectoForm
from proyecto.models import Proyecto,RolProyecto
from guardian.shortcuts import get_perms
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin


class RolListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar roles de proyecto de un proyecto en especifico.
    """
    template_name = 'change_list.html'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
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


class RolListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
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


class RolProyectoCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, CreateView):
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
        """
        El mensaje que aparece cuando se crea correctamente

        :param cleaned_data:
        :return:
        """
        return "Rol de Proyecto '{}' creado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        """
        El sitio donde se redirige al crear correctamente
        :return:
        """
        return reverse('proyecto_rol_list',kwargs=self.kwargs)

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de creacion

        :return:
        """
        kwargs = super(RolProyectoCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_rol_list',kwargs=self.kwargs),
            'proyecto_id': self.kwargs['proyecto_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
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
        """
        Se actualiza el nombre del group asociado para que no genere conflictos de unicidad

        :param form:
        :return:
        """
        rol = form.save(commit=False)
        rol.name = rol.nombre+rol.proyecto.id.__str__()
        return super().form_valid(form)


class RolProyectoUpdateView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, UpdateView):
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
            return super(RolProyectoUpdateView, self).check_permissions(request)
        except RolProyecto.DoesNotExist:
            raise Http404('no existe rol de proyecto con el id en la url')

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se edita correctamente

        :param cleaned_data:
        :return:
        """
        return "Rol de Proyecto '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        """
        El sitio donde se redirige al editar correctamente

        :return:
        """
        return reverse('proyecto_rol_list', args=(self.kwargs['proyecto_id'],))

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion

        :return:
        """
        kwargs = super(RolProyectoUpdateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
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
        """
        Se actualiza el nombre del group asociado para que no genere conflictos de unicidad

        :param form:
        :return:
        """
        rol = form.save(commit=False)
        rol.name = rol.nombre + rol.proyecto.id.__str__()
        print(rol.name)
        print(rol.nombre)

        return super().form_valid(form)


class RolPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
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
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
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


class RolEliminarView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, DeleteView):
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
        """
        El sitio donde se redirige al eliminar correctamente

        :return:
        """
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
            return super(RolEliminarView, self).check_permissions(request)
        except RolProyecto.DoesNotExist:
            raise Http404('no existe rol de proyecto con el id en la url')



    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se elimina correctamente

        :param cleaned_data:
        :return:
        """
        return "Rol eliminado exitosamente."

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
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
