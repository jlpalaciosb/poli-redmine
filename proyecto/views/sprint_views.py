from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoEstadoInvalidoMixin
from guardian.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, DeleteView
from proyecto.models import Sprint, Proyecto, ESTADOS_SPRINT, Flujo, UserStorySprint, Fase
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import  get_perms
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from guardian.decorators import permission_required
from proyecto.forms import MiembroSprintForm
from django.contrib.auth.decorators import login_required
from proyecto.decorators import proyecto_en_ejecucion

class SprintListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar sprints del proyecto
    """
    template_name = 'proyecto/sprint/change_list.html'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'
    estado = '*'  # estado de los USs a listar (* significa todos los estados)

    def dispatch(self, request, *args, **kwargs):
        self.estado = request.GET.get('estado', '*')
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(SprintListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Lista de Sprints de '+ proyecto.nombre
        context['crear_button'] = 'administrar_sprint' in get_perms(self.request.user, proyecto)
        context['crear_url'] = reverse('proyecto_sprint_crear',kwargs=self.kwargs)
        context['crear_button_text'] = 'Nuevo Sprint'

        # datatables
        context['nombres_columnas'] = ['id', 'Sprint Nro','Estado']
        context['order'] = [1, "des"]
        context['datatable_row_link'] = reverse('proyecto_sprint_administrar', args=(self.kwargs['proyecto_id'],99999))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('proyecto_sprint_list_json', kwargs=self.kwargs) + '?estado=' + self.estado
        context['selected'] = self.estado
        context['roles']=True
        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                   {'nombre':'Proyectos', 'url': reverse('proyectos')},
                    {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                    {'nombre': 'Sprints', 'url': '#'}
                   ]



        return context

class SprintListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista para devolver todos los sprint de un proyecto en formato JSON
    """
    model = Sprint
    columns = ['id', 'orden','estado']
    order_columns = ['id', 'orden','estado']
    max_display_length = 100
    permission_denied_message = 'No tiene permiso para ver Proyectos.'



    def get_initial_queryset(self):
        """
        Se sobreescribe el metodo para que la lista sean todos los sprints de un proyecto en particular
        :return:
        """
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        st = self.request.GET.get('estado', '*')
        if st == '1' or st == '2' or st == '3':
            return proyecto.sprint_set.filter(estado=ESTADOS_SPRINT[int(st)-1][0])

        return proyecto.sprint_set.all()

@login_required
@permission_required('proyecto.administrar_sprint',(Proyecto, 'id', 'proyecto_id'), return_403=True)
@proyecto_en_ejecucion
def crear_sprint(request, proyecto_id):
    """
    Vista para crear un sprint en caso de que se cumpla que a lo sumo exista un sprint planificado en el proyecto.
    El sprint a crear tendra la duracion que tiene el proyecto
    Se redirecciona a la lista de sprint
    :param request:
    :param proyecto_id: El id del proyecto
    :return:
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    orden = proyecto.sprint_set.all().count()
    if Sprint.objects.filter(proyecto=proyecto, estado='PLANIFICADO').count()!=0:
        messages.add_message(request, messages.WARNING, 'Ya hay un sprint en planificacion!')
        return HttpResponseRedirect(reverse('proyecto_sprint_list', args=(proyecto_id,)))
    try:
        sprint = Sprint.objects.create(proyecto=proyecto, duracion=proyecto.duracionSprint, estado='PLANIFICADO', orden=orden+1)
        messages.add_message(request, messages.SUCCESS, 'Se creo el sprint Nro '+str(orden+1))
        return HttpResponseRedirect(reverse('proyecto_sprint_list', args=(proyecto_id,)))
    except:
        messages.add_message(request, messages.ERROR, 'Ha ocurrido un error!')
        return HttpResponseRedirect(reverse('proyecto_sprint_list', args=(proyecto_id,)))

class SprintPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
           Vista Basada en Clases para la visualizacion del perfil de un sprint
    """
    model = Sprint
    context_object_name = 'sprint'
    template_name = 'proyecto/sprint/gestion_sprint.html'
    pk_url_kwarg = 'sprint_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(SprintPerfilView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Administrar Sprint'
        context['titulo_form_editar'] = 'Datos del Sprint'
        context['titulo_form_editar_nombre'] = context[SprintPerfilView.context_object_name].orden

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Administrar Sprint', 'url': '#'}
                                 ]

        return context


class FlujoSprintListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista para devolver todos los flujos de un sprint en un proyecto en formato JSON
    """
    model = Flujo
    columns = ['id', 'nombre']
    order_columns = ['id', 'nombre']
    max_display_length = 100
    permission_denied_message = 'No tiene permiso para ver Proyectos.'

    def get_initial_queryset(self):
        try:
            sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
            return sprint.flujos_sprint()
        except Sprint.DoesNotExist:
            return

class FlujoSprintListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar flujos de un sprint en un proyecto
    """
    template_name = 'change_list.html'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(FlujoSprintListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context = super(FlujoSprintListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Seleccione un flujo para visualizar su tablero'
        context['crear_button'] = False

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre Flujo']
        context['order'] = [1, "des"]
        context['datatable_row_link'] = reverse('proyecto_sprint_tablero', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id'],99999))
        context['list_json'] = reverse('proyecto_sprint_flujos_json', kwargs=self.kwargs)
        context['roles'] = True


        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Administrar Sprint', 'url': reverse('proyecto_sprint_administrar',kwargs=self.kwargs)},
                                 {'nombre': 'Flujos', 'url':'#'}
                                 ]


        return context

class TableroKanbanView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
           Vista Basada en Clases para la visualizacion del tablero kanban
    """
    model = Sprint
    context_object_name = 'sprint'
    template_name = 'proyecto/sprint/tablera_kanban.html'
    pk_url_kwarg = 'sprint_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(TableroKanbanView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        try:
            flujo = Flujo.objects.get(pk=self.kwargs['flujo_id'])
            context['flujo'] = flujo
            sprint = context['sprint']
            context['user_stories_sprint'] = UserStorySprint.objects.filter(sprint=sprint, us__flujo=flujo)
        except Flujo.DoesNotExist:
            raise Http404('No existe dicho flujo')
        context['titulo'] = 'Tablero Kanban'


        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Administrar Sprint',
                                  'url': reverse('proyecto_sprint_administrar', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id']))},
                                 {'nombre': 'Flujos', 'url': reverse('proyecto_sprint_flujos', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id']))},
                                 {'nombre':'Tablero Kanban', 'url':'#'}
                                 ]

        return context

@login_required
@proyecto_en_ejecucion
def mover_us_kanban(request, proyecto_id, sprint_id, flujo_id, us_id):
    """
    Vista para mover un user story a un estado
    :param request:
    :param proyecto_id: El id del proyecto
    :return:
    """

    try:
        sprint = Sprint.objects.get(pk=sprint_id)
        user_story_sprint = UserStorySprint.objects.get(sprint=sprint, us_id=us_id)
        movimiento = int(request.GET.get('movimiento'))
        if not request.user == user_story_sprint.asignee.miembro.user:
            # Si no es el asignado entonces se le deniega el permiso
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id,sprint_id,flujo_id)))
        if movimiento is None and (movimiento != 1 or movimiento != -1):
            #Si el moviemiento recibido como parametro no es valido
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))

        if user_story_sprint.fase_sprint == user_story_sprint.us.flujo.cantidadFases and user_story_sprint.estado_fase_sprint=='DONE' and movimiento == 1:
            #Si se encuentra en el DONE de la ultima fase y quiere moverse al siguiente estado entonces es incorrecto
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))
        if user_story_sprint.fase_sprint == 1 and user_story_sprint.estado_fase_sprint=='TODO' and movimiento == -1:
            #Si se encuentra en el TO DO  de la primera fase y quiere moverse al estado anterior entonces es incorrecto
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))
        if movimiento == 1:
            if user_story_sprint.estado_fase_sprint == 'TODO':
                user_story_sprint.estado_fase_sprint = 'DOING'

            elif user_story_sprint.estado_fase_sprint == 'DOING':
                user_story_sprint.estado_fase_sprint = 'DONE'

            elif user_story_sprint.estado_fase_sprint == 'DONE':
                user_story_sprint.fase_sprint = Fase.objects.get(flujo = user_story_sprint.us.flujo, orden = user_story_sprint.fase_sprint.orden + 1)
                user_story_sprint.estado_fase_sprint = 'TODO'

        else:

            if user_story_sprint.estado_fase_sprint == 'TODO':
                user_story_sprint.fase_sprint = Fase.objects.get(flujo=user_story_sprint.us.flujo,
                                                                 orden=user_story_sprint.fase_sprint.orden - 1)
                user_story_sprint.estado_fase_sprint = 'DONE'

            elif user_story_sprint.estado_fase_sprint == 'DOING':
                user_story_sprint.estado_fase_sprint = 'TODO'

            elif user_story_sprint.estado_fase_sprint == 'DONE':
                user_story_sprint.estado_fase_sprint = 'DOING'
        user_story_sprint.save()

        return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))

    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))


