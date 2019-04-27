from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, SuccessMessageOnDeleteMixin, ProyectoEstadoInvalidoMixin
from guardian.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, DeleteView
from proyecto.models import TipoUS, Proyecto
from proyecto.forms import TipoUsForm, CampoPersonalizadoFormSet
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse
from django.db import transaction
from guardian.shortcuts import  get_perms
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect


class TipoUsCreateView(LoginRequiredMixin, PermisosPorProyectoMixin,ProyectoEstadoInvalidoMixin , SuccessMessageMixin, CreateView):
    """
    Vista para creacion de tipo de us. Se permiten hasta 5 campos personalizados
    """
    permission_required = ['proyecto.add_tipous']
    model = TipoUS
    form_class = TipoUsForm
    template_name = 'proyecto/tipous/change_form.html'

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            #La instancia del tipo de US va ser uno cuyo proyecto sea aquel que le corresponda el id del request
            kwargs.update({'instance' : TipoUS(proyecto=Proyecto.objects.get(pk=self.kwargs['proyecto_id'])),
                           'success_url': reverse('proyecto_tipous_list', kwargs=self.kwargs)

                           })
            return kwargs
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')

    def form_valid(self, form):

        context = self.get_context_data()
        campospersonalizados = context['campospersonalizados']
        with transaction.atomic():
            self.object = form.save()
            if campospersonalizados.is_valid():
                campospersonalizados.instance = self.object
                campospersonalizados.save()
        return super(TipoUsCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('proyecto_tipous_list', kwargs=self.kwargs)

    def get_success_message(self, cleaned_data):
        return "Tipo de US '{}' creado exitosamente.".format(cleaned_data['nombre'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Tipos de US'
        context['titulo_form_crear'] = 'Insertar Datos del Tipo de US'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Tipos de US', 'url': reverse('proyecto_tipous_list', kwargs=self.kwargs)},
                                 {'nombre': 'Crear', 'url': '#'}
                                 ]
        if self.request.POST:
            context['campospersonalizados'] = CampoPersonalizadoFormSet(self.request.POST)
        else:
            context['campospersonalizados'] = CampoPersonalizadoFormSet()
        return context

class TipoUsUpdateView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEstadoInvalidoMixin, SuccessMessageMixin, UpdateView):
    """
    Vistas para modificar un Tipo de US. No se permite acceder a esta vista si al menos un user story tiene asociado este tipo de us.
    """
    permission_required = 'proyecto.change_tipous'
    model = TipoUS
    pk_url_kwarg = 'tipous_id'
    form_class = TipoUsForm
    template_name = 'proyecto/tipous/change_form.html'
    context_object_name = 'tipous'

    def check_permissions(self, request):
        """
        Se sobreescribe el metodo para no permitir la modificacion de un tipo de us si algun US ya tiene asociado el tipo de us
        :param request:
        :return:
        """
        try:
            tipous = TipoUS.objects.get(pk=self.kwargs['tipous_id'])
            if tipous.userstory_set.all():
               return self.handle_no_permission()
            return super(TipoUsUpdateView, self).check_permissions(request)
        except TipoUS.DoesNotExist:
            raise Http404('no existe tipo de us con el id en la url')


    def get_success_url(self):
        return reverse('proyecto_tipous_ver', kwargs=self.kwargs)

    def get_success_message(self, cleaned_data):
        return "Tipo de US '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_context_data(self, **kwargs):
        context = super(TipoUsUpdateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Editar Tipo de US'
        context['titulo_form_editar'] = 'Datos del Tipo de US'
        context['titulo_form_editar_nombre'] = context[TipoUsUpdateView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Tipos de US', 'url': reverse('proyecto_tipous_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Ver Tipo de US', 'url': reverse('proyecto_tipous_ver', kwargs=self.kwargs)},
                                 {'nombre': 'Editar', 'url': '#'}
                                 ]
        if self.request.POST:
            context['campospersonalizados'] = CampoPersonalizadoFormSet(self.request.POST, instance=self.object)
        else:
            context['campospersonalizados'] = CampoPersonalizadoFormSet(instance=self.object)
        return context

    def form_valid(self, form):

        context = self.get_context_data()
        campospersonalizados = context['campospersonalizados']
        with transaction.atomic():
            self.object = form.save()
            if campospersonalizados.is_valid():
                campospersonalizados.instance = self.object
                campospersonalizados.save()
        return super(TipoUsUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            #La instancia del tipo de US va ser uno cuyo proyecto sea aquel que le corresponda el id del request
            kwargs.update({
                           'success_url': reverse('proyecto_tipous_ver', kwargs=self.kwargs)
                           })
            return kwargs
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')

class TipoUsListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar tipos de us del proyecto de un proyecto en especifico.
    """
    template_name = 'change_list.html'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(TipoUsListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Lista de Tipos de US '+ proyecto.nombre
        context['crear_button'] = 'add_tipous' in get_perms(self.request.user, proyecto)
        context['crear_url'] = reverse('proyecto_tipous_crear',kwargs=self.kwargs)
        context['crear_button_text'] = 'Nuevo Tipo US'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('proyecto_tipous_ver', args=(self.kwargs['proyecto_id'],99999))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('proyecto_tipous_list_json', kwargs=self.kwargs)
        context['roles']=True
        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Proyectos', 'url': reverse('proyectos')},
                    {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                    {'nombre': 'Tipos de US', 'url': '#'}
                   ]



        return context

class TipoUsListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista para devolver todos los tipos de us de un proyecto en formato JSON
    """
    model = TipoUS
    columns = ['id', 'nombre']
    order_columns = ['id', 'nombre']
    max_display_length = 100
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def get_initial_queryset(self):
        """
        Se sobreescribe el metodo para que la lista sean todos los tipos de us de un proyecto en particular
        :return:
        """
        proyecto=Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        return proyecto.tipous_set.all()

class TipoUSPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
           Vista Basada en Clases para la visualizacion del perfil de un tipo de us
    """
    model = TipoUS
    context_object_name = 'tipous'
    template_name = 'proyecto/tipous/tipous_perfil.html'
    pk_url_kwarg = 'tipous_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(TipoUSPerfilView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Ver Tipo de US'
        context['titulo_form_editar'] = 'Datos del Tipo de US'
        context['titulo_form_editar_nombre'] = context[TipoUSPerfilView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Tipos de US',
                                  'url': reverse('proyecto_tipous_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Ver Tipo de US', 'url': '#'}
                                 ]

        return context

class TipoUsEliminarView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEstadoInvalidoMixin, SuccessMessageOnDeleteMixin, DeleteView):
    """
    Vista que elimina un TIPO DE US en caso que tenga los permisos necesarios y que no este asociado con ningun user story
    """
    model = TipoUS
    context_object_name = 'tipous'
    template_name = 'proyecto/tipous/tipous_eliminar.html'
    pk_url_kwarg = 'tipous_id'
    permission_required = 'proyecto.delete_tipous'
    permission_denied_message = 'No tiene permiso para eliminar el tipo de us.'
    success_message = 'Tipo de US eliminado correctamente'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_url(self):
        return reverse('proyecto_tipous_list', args=(self.kwargs['proyecto_id'],))


    def get_success_message(self, cleaned_data):
        return "Tipo de US eliminado exitosamente."

    def get_context_data(self, **kwargs):
        context = super(TipoUsEliminarView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Eliminar Tipo de US'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Tipos de US', 'url': reverse('proyecto_tipous_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': context[self.context_object_name].nombre, 'url': reverse('proyecto_tipous_ver', args=(self.kwargs['proyecto_id'],self.kwargs['tipous_id']))},
            {'nombre': 'Eliminar', 'url': '#'}
        ]
        context['eliminable'] = self.eliminable()
        return context

    def eliminable(self):
        """
        Si un tipo de us esta asociado con al menos un user story entonces no se puede eliminar.
        :return:
        """
        return not self.get_object().userstory_set.all()

    def post(self, request, *args, **kwargs):
        if self.eliminable():
            return super(TipoUsEliminarView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.success_url)

