from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoEnEjecucionMixin
from guardian.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView
from proyecto.models import Sprint, Proyecto, MiembroSprint
from django.http import  HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from guardian.shortcuts import  get_perms
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from proyecto.forms import MiembroSprintForm, CambiarMiembroForm
from django.contrib import messages
from guardian.decorators import permission_required
from proyecto.decorators import proyecto_en_ejecucion
from django.contrib.auth.decorators import login_required

class MiembroSprintListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar miembros de un sprint del proyecto
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
        context = super(MiembroSprintListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        context['titulo'] = 'Lista de Miembros de Sprints de '+ proyecto.nombre
        context['crear_button'] = 'administrar_sprint' in get_perms(self.request.user, proyecto) and sprint.estado == 'PLANIFICADO'
        # TODO: Cambiar a agregar miembro sprint
        context['crear_url'] = reverse('proyecto_sprint_miembros_agregar', kwargs=self.kwargs)
        context['crear_button_text'] = 'Agregar miembro'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre','Horas Asignadas']
        context['order'] = [1, "des"]
        #TODO: Cambiar a ver miembro de sprint
        context['datatable_row_link'] = reverse('proyecto_sprint_miembros_ver', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id'],99999))  # pasamos inicialmente el id 1
        # TODO: Cambiar a json de miembro sprint
        context['list_json'] = reverse('proyecto_sprint_miembros_json', kwargs=self.kwargs)

        context['roles']=True
        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                                {'nombre':'Proyectos', 'url': reverse('proyectos')},
                                {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                {'nombre': 'Sprints',
                                'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
                                 {'nombre': 'Miembros', 'url': '#'}
                   ]



        return context

class MiembroSprintListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista para devolver todos los miembros de un sprint del proyecto en formato JSON
    """
    model = MiembroSprint
    columns = ['id', 'miembro.user.username','horasAsignadas']
    order_columns = ['id', 'miembro.user.username','horasAsignadas']
    max_display_length = 100
    permission_denied_message = 'No tiene permiso para ver Proyectos.'



    def get_initial_queryset(self):
        """
        Se sobreescribe el metodo para que la lista sean todos los miembros sean de un sprint en un proyecto en particular
        :return:
        """
        try:
            sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'],proyecto__id=self.kwargs['proyecto_id'])
            return sprint.miembrosprint_set.all()
        except Sprint.DoesNotExist:
            return MiembroSprint.objects.none()

class MiembroSprintCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, SuccessMessageMixin, CreateView):
    """
    Vista para creacion de un miembro de sprint solo es valido si el sprint esta en estado pendiente
    """
    model = MiembroSprint
    template_name = "change_form.html"
    form_class = MiembroSprintForm
    permission_required = 'proyecto.administrar_sprint'
    permission_denied_message = 'No tiene permiso para administrar sprint.'

    def check_permissions(self, request):
        """
        Si el sprint no esta PLANIFICADO no se puede acceder a esta vista
        :param request:
        :return:
        """
        try:
            sprint = Sprint.objects.get(pk = self.kwargs['sprint_id'])
            if sprint.estado != 'PLANIFICADO':
                return HttpResponseForbidden()
            return super(MiembroSprintCreateView, self).check_permissions(request)
        except Sprint.DoesNotExist:
            return HttpResponseForbidden()
        except:
            return HttpResponseForbidden()


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se crea correctamente

        :param cleaned_data:
        :return:
        """
        return "Miembro de Sprint agregado exitosamente."

    def get_success_url(self):
        """
        El sitio donde se redirige al agregar correctamente
        :return:
        """
        return reverse('proyecto_sprint_miembros',kwargs=self.kwargs)

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de creacion
        :return:
        """
        kwargs = super(MiembroSprintCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_sprint_miembros',kwargs=self.kwargs),
            'proyecto_id': self.kwargs['proyecto_id'],
            'sprint_id': self.kwargs['sprint_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super(MiembroSprintCreateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        context['titulo'] = 'Miembros de Sprint'
        context['titulo_form_crear'] = 'Agregar Miembro al sprint'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden,
                                  'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
                                 {'nombre': 'Miembros', 'url': reverse('proyecto_sprint_miembros',kwargs=self.kwargs)},
                                 {'nombre': 'Crear', 'url':'#'}
                                 ]

        return context

    def form_valid(self, form):
        """
        Se actualiza la capacidad del sprint cuando se agrega correctamente
        :param form:
        :return:
        """
        response = super(MiembroSprintCreateView, self).form_valid(form)
        sprint = form.instance.sprint
        sprint.capacidad = sprint.capacidad + sprint.duracion*sprint.proyecto.diasHabiles*form.cleaned_data['horasAsignadas']
        sprint.save()
        return response

class MiembroSprintPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
           Vista Basada en Clases para la visualizacion del perfil de un miembro de un sprint
    """
    model = MiembroSprint
    context_object_name = 'miembro_sprint'
    template_name = 'proyecto/miembroSprint/miembro_sprint_perfil.html'
    pk_url_kwarg = 'miembroSprint_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super(MiembroSprintPerfilView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        miembro_sprint = MiembroSprint.objects.get(pk=self.kwargs['miembroSprint_id'])
        context['titulo'] = 'Ver Miembro del Sprint'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden,
                                  'url': reverse('proyecto_sprint_administrar', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id']))},
                                 {'nombre': 'Miembros',
                                  'url': reverse('proyecto_sprint_miembros', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id']))},
                                 {'nombre': miembro_sprint.miembro.user.username, 'url': '#'}
                                 ]

        return context

class MiembroSprintUpdateView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, SuccessMessageMixin, UpdateView):
    """
    Vista para cambiar horas de asignadas a un miembro de sprint. Solo es valido si el sprint esta pendiente. Se actualiza la capacidad del sprint
    """
    model = MiembroSprint
    template_name = "change_form.html"
    form_class = MiembroSprintForm
    permission_required = 'proyecto.administrar_sprint'
    permission_denied_message = 'No tiene permiso para administrar sprint.'
    pk_url_kwarg = 'miembroSprint_id'
    context_object_name = 'miembro_sprint'

    def check_permissions(self, request):
        """
        Si el sprint no esta PLANIFICADO no se puede acceder a esta vista
        :param request:
        :return:
        """
        try:
            sprint = Sprint.objects.get(pk = self.kwargs['sprint_id'])
            if sprint.estado != 'PLANIFICADO':
                return HttpResponseForbidden()
            return super(MiembroSprintUpdateView, self).check_permissions(request)
        except Sprint.DoesNotExist:
            return HttpResponseForbidden()
        except:
            return HttpResponseForbidden()


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se crea correctamente

        :param cleaned_data:
        :return:
        """
        return "Miembro de Sprint agregado exitosamente."

    def get_success_url(self):
        """
        El sitio donde se redirige al modificar correctamente
        :return:
        """
        return reverse('proyecto_sprint_miembros_ver',args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id'], self.kwargs['miembroSprint_id']))

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion
        :return:
        """
        kwargs = super(MiembroSprintUpdateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
            'sprint_id': self.kwargs['sprint_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """
        context = super(MiembroSprintUpdateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        miembro_sprint = MiembroSprint.objects.get(pk=self.kwargs['miembroSprint_id'])
        context['titulo'] = 'Editar Miembro de Sprint'
        context['titulo_form_editar'] = 'Datos del Miembro de Sprint'
        context['titulo_form_editar_nombre'] = context[MiembroSprintUpdateView.context_object_name].miembro

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden,
                                  'url': reverse('proyecto_sprint_administrar',
                                                 args=(self.kwargs['proyecto_id'], self.kwargs['sprint_id']))},
                                 {'nombre': 'Miembros',
                                  'url': reverse('proyecto_sprint_miembros',
                                                 args=(self.kwargs['proyecto_id'], self.kwargs['sprint_id']))},
                                 {'nombre': miembro_sprint.miembro.user.username, 'url': reverse('proyecto_sprint_miembros_ver', kwargs=self.kwargs)},
                                 {'nombre': 'Modificar', 'url':'#'}
                                 ]

        return context

    def form_valid(self, form):
        """
        Se actualiza la capacidad del sprint cuando se modifica las horas asignadas de un miembro
        :param form:
        :return:
        """
        response = super(MiembroSprintUpdateView, self).form_valid(form)
        sprint = form.instance.sprint
        sprint.capacidad = sprint.capacidad - sprint.duracion * sprint.proyecto.diasHabiles * form.initial['horasAsignadas']
        sprint.capacidad = sprint.capacidad + sprint.duracion*sprint.proyecto.diasHabiles*form.cleaned_data['horasAsignadas']
        sprint.save()
        return response

class MiembroSprintIntercambiarView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, SuccessMessageMixin, UpdateView):
    """
    Vista para intercanmbiar un miembro de sprint en ejecucion. Solo es valido si el sprint esta EJECUCION. Se actualiza la capacidad del sprint
    """
    model = MiembroSprint
    template_name = "change_form.html"
    form_class = CambiarMiembroForm
    permission_required = 'proyecto.administrar_sprint'
    permission_denied_message = 'No tiene permiso para administrar sprint.'
    pk_url_kwarg = 'miembroSprint_id'
    context_object_name = 'miembro_sprint'

    def check_permissions(self, request):
        """
        Si el sprint no esta EN EJECUCION no se puede acceder a esta vista
        :param request:
        :return:
        """
        try:
            sprint = Sprint.objects.get(pk = self.kwargs['sprint_id'])
            if sprint.estado != 'EN_EJECUCION':
                return HttpResponseForbidden()
            return super(MiembroSprintIntercambiarView, self).check_permissions(request)
        except Sprint.DoesNotExist:
            return HttpResponseForbidden()
        except:
            return HttpResponseForbidden()


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se intercambia correctamente

        :param cleaned_data:
        :return:
        """
        return "Miembro de Sprint intercambiado exitosamente."

    def get_success_url(self):
        """
        El sitio donde se redirige al cambiar correctamente
        :return:
        """
        return reverse('proyecto_sprint_miembros',args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id']))

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion
        :return:
        """
        kwargs = super(MiembroSprintIntercambiarView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_sprint_miembros',args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id'])),
            'proyecto_id': self.kwargs['proyecto_id'],
            'sprint_id': self.kwargs['sprint_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template
        :param kwargs:
        :return:
        """

        context = super(MiembroSprintIntercambiarView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        miembro_sprint = MiembroSprint.objects.get(pk=self.kwargs['miembroSprint_id'])
        context['titulo'] = 'Intercambiar miembro de Sprint'
        context['titulo_form_editar'] = 'Datos del Miembro a excluir del Sprint'
        context['titulo_form_editar_nombre'] = context[MiembroSprintUpdateView.context_object_name].miembro

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden,
                                  'url': reverse('proyecto_sprint_administrar',
                                                 args=(self.kwargs['proyecto_id'], self.kwargs['sprint_id']))},
                                 {'nombre': 'Miembros',
                                  'url': reverse('proyecto_sprint_miembros',
                                                 args=(self.kwargs['proyecto_id'], self.kwargs['sprint_id']))},
                                 {'nombre': miembro_sprint.miembro.user.username, 'url': reverse('proyecto_sprint_miembros_ver', kwargs=self.kwargs)},
                                 {'nombre': 'Intercambiar', 'url':'#'}
                                 ]

        return context


@login_required
@permission_required('proyecto.administrar_sprint',(Proyecto, 'id', 'proyecto_id'), return_403=True)
@proyecto_en_ejecucion
def excluir_miembro_sprint(request, miembroSprint_id, sprint_id, proyecto_id):
    """
    Vista para excluir a un miembro de un sprint que esta planficado
    :param request:
    :param miembroSprint_id:
    :param sprint_id:
    :param proyecto_id:
    :return:
    """
    try:
        miembro = MiembroSprint.objects.get(pk=miembroSprint_id,sprint_id=sprint_id)
        sprint = miembro.sprint
        if sprint.estado != 'PLANIFICADO':
            raise Exception('Sprint no esta planificado')
        if miembro.userstorysprint_set.all().count() > 0:
            raise Exception('El miembro tiene al menos un User Story asignado')
        sprint.capacidad = sprint.capacidad - sprint.duracion * sprint.proyecto.diasHabiles * miembro.horasAsignadas
        miembro.delete()
        sprint.save()
        messages.add_message(request,messages.SUCCESS,'Se ha excluido al usuario del sprint')

    except MiembroSprint.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'No existe el miembro a excluir!')

    except Exception as e:
        messages.add_message(request, messages.ERROR, e.args[0])
    finally:
        return HttpResponseRedirect(reverse('proyecto_sprint_miembros', args=(proyecto_id, sprint_id)))



