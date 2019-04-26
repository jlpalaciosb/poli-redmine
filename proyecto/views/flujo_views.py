from proyecto.forms import FlujoForm, FaseFormSet
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, SuccessMessageOnDeleteMixin, ProyectoEstadoInvalidoMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, DeleteView
from proyecto.models import Flujo, Proyecto
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse
from django.db import transaction
from guardian.shortcuts import get_perms
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect


class FlujoCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEstadoInvalidoMixin, SuccessMessageMixin, CreateView):
    """
    Vista para creacion de flujo.
    """
    permission_required = ['proyecto.add_flujo']
    model = Flujo
    form_class = FlujoForm
    template_name = 'proyecto/flujo/change_form.html'

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            # La instancia del flujo va ser uno cuyo proyecto sea aquel que le corresponda el id del request
            kwargs.update({'instance': Flujo(proyecto=Proyecto.objects.get(pk=self.kwargs['proyecto_id'])),
                           'success_url': reverse('proyecto_flujo_list', kwargs=self.kwargs)

                           })
            return kwargs
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')

    def get_success_url(self):
        return reverse('proyecto_flujo_list', kwargs=self.kwargs)

    def get_success_message(self, cleaned_data):
        return "Flujo '{}' creado exitosamente.".format(cleaned_data['nombre'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Flujo'
        context['titulo_form_crear'] = 'Insertar Datos del Flujo'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Flujo', 'url': reverse('proyecto_flujo_list', kwargs=self.kwargs)},
                                 {'nombre': 'Crear', 'url': '#'}
                                 ]
        if self.request.POST:
            context['fases'] = FaseFormSet(self.request.POST)
        else:
            context['fases'] = FaseFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        fase = context['fases']
        with transaction.atomic():
            self.object = form.save()
            if fase.is_valid():
                fase.instance = self.object
                fase.save()
        return super(FlujoCreateView, self).form_valid(form)


class FlujoUpdateView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEstadoInvalidoMixin, SuccessMessageMixin, UpdateView):
    """
    Vistas para modificar un flujo. No se permite acceder a esta vista si al menos un proyecto tengo asociado este flujo.
    """
    permission_required = 'proyecto.change_flujo'
    model = Flujo
    pk_url_kwarg = 'flujo_id'
    form_class = FlujoForm
    template_name = 'proyecto/flujo/change_form.html'
    context_object_name = 'flujo'

    def check_permissions(self, request):
        """
        Se sobreescribe el metodo para no permitir la modificacion de un flujo si algun user story ya tiene asociado el flujo
        :param request:
        :return:
        """
        try:
            flujo = Flujo.objects.get(pk=self.kwargs['flujo_id'])
            cantidadUserStoryAsociados = flujo.userstory_set.all().count()
            if cantidadUserStoryAsociados > 0 :
                return HttpResponseForbidden()
            return super(FlujoUpdateView, self).check_permissions(request)
        except Flujo.DoesNotExist:
            raise Http404('no existe flujo con el id en la url')

    def get_success_url(self):
        return reverse('proyecto_flujo_ver', kwargs=self.kwargs)

    def get_success_message(self, cleaned_data):
        return "Flujo '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_context_data(self, **kwargs):
        context = super(FlujoUpdateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Editar Flujo'
        context['titulo_form_editar'] = 'Datos del flujo'
        context['titulo_form_editar_nombre'] = context[FlujoUpdateView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Flujo',
                                  'url': reverse('proyecto_flujo_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Ver flujo', 'url': reverse('proyecto_flujo_ver', kwargs=self.kwargs)},
                                 {'nombre': 'Editar', 'url': '#'}
                                 ]
        if self.request.POST:
            context['fases'] = FaseFormSet(self.request.POST, instance=self.object)
        else:
            context['fases'] = FaseFormSet(instance=self.object)
        return context

    def form_valid(self, form):

        context = self.get_context_data()
        fase = context['fases']
        with transaction.atomic():
            self.object = form.save()
            if fase.is_valid():
                fase.instance = self.object
                fase.save()
        return super(FlujoUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            # La instancia del flujo va ser uno cuyo proyecto sea aquel que le corresponda el id del request
            kwargs.update({
                'success_url': reverse('proyecto_flujo_ver', kwargs=self.kwargs)
            })
            return kwargs
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')


class FlujoListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar Flujos del proyecto de un proyecto en especifico.
    """
    template_name = 'change_list.html'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(FlujoListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Lista de Flujo ' + proyecto.nombre
        context['crear_button'] = 'add_flujo' in get_perms(self.request.user, proyecto)
        context['crear_url'] = reverse('proyecto_flujo_crear', kwargs=self.kwargs)
        context['crear_button_text'] = 'Nuevo Flujo'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre']
        context['order'] = [1, "asc"]
        context['datatable_row_link'] = reverse('proyecto_flujo_ver', args=(
        self.kwargs['proyecto_id'], 99999))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('proyecto_flujo_list_json', kwargs=self.kwargs)
        context['roles'] = True
        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Flujo', 'url': '#'}
                                 ]

        return context


class FlujoListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista para devolver todos los Flujo de un proyecto en formato JSON
    """
    model = Flujo
    columns = ['id', 'nombre']
    order_columns = ['id', 'nombre']
    max_display_length = 100
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def get_initial_queryset(self):
        """
        Se sobreescribe el metodo para que la lista sean todos los Flujo de un proyecto en particular
        :return:
        """
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        return proyecto.flujo_set.all()


class FlujoPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
           Vista Basada en Clases para la visualizacion del perfil de un flujo
    """
    model = Flujo
    context_object_name = 'flujo'
    template_name = 'proyecto/flujo/flujo_perfil.html'
    pk_url_kwarg = 'flujo_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(FlujoPerfilView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Ver flujo'
        context['titulo_form_editar'] = 'Datos del flujo'
        context['titulo_form_editar_nombre'] = context[FlujoPerfilView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Flujo',
                                  'url': reverse('proyecto_flujo_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Ver flujo', 'url': '#'}
                                 ]

        return context


class FlujoEliminarView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEstadoInvalidoMixin, SuccessMessageOnDeleteMixin, DeleteView):
    """
    Vista que elimina un flujo en caso que tenga los permisos necesarios y que no este asociado con ningun user story
    """
    model = Flujo
    context_object_name = 'flujo'
    template_name = 'proyecto/flujo/flujo_eliminar.html'
    pk_url_kwarg = 'flujo_id'
    permission_required = 'proyecto.delete_flujo'
    permission_denied_message = 'No tiene permiso para eliminar el flujo.'
    success_message = 'flujo eliminado correctamente'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_url(self):
        return reverse('proyecto_flujo_list', args=(self.kwargs['proyecto_id'],))

    def get_success_message(self, cleaned_data):
        return "Flujo eliminado exitosamente."

    def get_context_data(self, **kwargs):
        context = super(FlujoEliminarView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Eliminar flujo'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Flujo',
                                  'url': reverse('proyecto_flujo_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': context[self.context_object_name].nombre,
                                  'url': reverse('proyecto_flujo_ver',
                                                 args=(self.kwargs['proyecto_id'], self.kwargs['flujo_id']))},
                                 {'nombre': 'Eliminar', 'url': '#'}
                                 ]
        context['eliminable'] = self.eliminable()
        return context

    def eliminable(self):
        """
        Si un flujo esta asociado con al menos un user story entonces no se puede eliminar.
        :return:
        """
        flujo = Flujo.objects.get(pk=self.kwargs['flujo_id'])
        cantidadUserStoryAsociados = flujo.userstory_set.all().count()
        if cantidadUserStoryAsociados > 0:
            return False
        return True

    def post(self, request, *args, **kwargs):
        if self.eliminable():
            return super(FlujoEliminarView, self).post(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.success_url)

