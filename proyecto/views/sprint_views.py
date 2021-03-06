import datetime
from io import BytesIO

from ProyectoIS2_9.utils import notificar_revision, notificar_inicio_sprint

from ProyectoIS2_9 import settings
from proyecto.forms.sprint_us_forms import SprintCambiarEstadoForm
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoEstadoInvalidoMixin
from guardian.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, TemplateView, DetailView, DeleteView
from proyecto.models import Sprint, Proyecto, ESTADOS_SPRINT, Flujo, UserStorySprint, Fase, MiembroSprint, UserStory, \
    ESTADOS_US_PROYECTO
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.db import transaction

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from django.views.generic import View
from reportlab.platypus import Table, TableStyle

from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import  get_perms
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib import messages
from django.http import HttpResponseRedirect
from guardian.decorators import permission_required
from django.contrib.auth.decorators import login_required
from proyecto.decorators import proyecto_en_ejecucion
from django.db import models
from proyecto.models import Actividad
from django.contrib.messages.views import SuccessMessageMixin

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
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(SprintListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Sprints del Proyecto'
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

@login_required
@permission_required('proyecto.administrar_sprint',(Proyecto, 'id', 'proyecto_id'), return_403=True)
@proyecto_en_ejecucion
def iniciar_sprint(request, proyecto_id, sprint_id):
    """
    Vista para iniciar un sprint en caso de que se cumpla que a lo sumo exista un US en el sprint.
    El sprint solo podra ser iniciado si no existe otro sprint en ejecucion en el proyecto
    Se redirecciona a la lista de sprint
    :param request:
    :param proyecto_id: El id del proyecto
    :param sprint_orden: El orden del sprint dentro del proyecto
    :return:
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    sprint = Sprint.objects.get(pk=sprint_id)
    if Sprint.objects.filter(proyecto=proyecto, estado='EN_EJECUCION').count()!=0:
        messages.add_message(request, messages.WARNING, 'Ya hay un sprint en ejecucion!')
        return HttpResponseRedirect(reverse('proyecto_sprint_administrar', args=(proyecto_id, sprint.id)))
    elif UserStorySprint.objects.filter(sprint=sprint_id).count()==0:
        messages.add_message(request, messages.WARNING, 'Se debe tener al menos un US en el Sprint!')
        return HttpResponseRedirect(reverse('proyecto_sprint_administrar', args=(proyecto_id, sprint.id)))
    elif not sprint.es_dia_permitido():
        messages.add_message(request, messages.WARNING, 'No se puede realizar esta operacion debido a que no es un dia habil de la semana!')
        return HttpResponseRedirect(reverse('proyecto_sprint_administrar', args=(proyecto_id, sprint.id)))
    try:
        sprint.estado='EN_EJECUCION'
        sprint.fechaInicio=datetime.date.today()
        horas = 0
        for usp in sprint.userstorysprint_set.all():
            horas = horas + usp.tiempo_planificado_sprint
        sprint.total_horas_planificadas = horas
        sprint.save()
        messages.add_message(request, messages.SUCCESS, 'Se inicio el sprint Nro '+str(sprint.orden))
        notificar_inicio_sprint(sprint)
        messages.add_message(request, messages.SUCCESS, 'Se notificó a los miembros')
        return HttpResponseRedirect(reverse('proyecto_sprint_administrar', args=(proyecto_id,sprint_id)))
    except:
        messages.add_message(request, messages.ERROR, 'Ha ocurrido un error!')
        return HttpResponseRedirect(reverse('proyecto_sprint_administrar', args=(proyecto_id,sprint_id)))


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
        messages.add_message(request, messages.WARNING, 'Ya hay un sprint en planificación!')
        return HttpResponseRedirect(reverse('proyecto_sprint_list', args=(proyecto_id,)))
    try:
        sprint = Sprint.objects.create(proyecto=proyecto, duracion=proyecto.duracionSprint, estado='PLANIFICADO', orden=orden+1, cant_dias_habiles=proyecto.diasHabiles)
        messages.add_message(request, messages.SUCCESS, 'Se creó el sprint Nro '+str(orden+1))
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
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(SprintPerfilView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        uss_total = UserStorySprint.objects.filter(sprint=sprint).count()
        uss_iniciados = uss_total - UserStorySprint.objects.filter(estado_fase_sprint='TODO', fase_sprint__orden=1, sprint=sprint).count()#CANTIDAD DE USER STORIES AUN SIN INICIAR
        uss_revision = UserStorySprint.objects.filter(us__estadoProyecto=6, sprint=sprint).count()
        uss_terminados = UserStorySprint.objects.filter(us__estadoProyecto=5, sprint=sprint).count()
        context['uss_total'] = uss_total
        context['uss_iniciados'] = uss_iniciados
        context['uss_revision'] = uss_revision
        context['uss_terminados'] = uss_terminados
        context['titulo_form_editar'] = 'Datos del Sprint'
        context['titulo_form_editar_nombre'] = context[SprintPerfilView.context_object_name].orden
        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden, 'url': '#'}
                                 ]

        return context

class SprintNoSePuedeCerrar(object):
    """
    Un sprint no se puede cerrar si hay al menos un user story que este en revision
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
            for us_sprint in sprint.userstorysprint_set.all():
                if us_sprint.us.estadoProyecto == 6:#Si al menos un user story esta en revision no se permite cerrar
                    messages.add_message(request,messages.WARNING,'Debe controlar todos los user stories en revision!')
                    return HttpResponseRedirect(reverse('proyecto_sprint_administrar',kwargs=self.kwargs))
            return super(SprintNoSePuedeCerrar, self).dispatch(request, *args, **kwargs)
        except Sprint.DoesNotExist:
            raise Http404('No existe dicho sprint')


class SprintCambiarEstadoView(LoginRequiredMixin, PermisosPorProyectoMixin, SprintNoSePuedeCerrar,SuccessMessageMixin, UpdateView):
    """
    Vista Basada en Clases para la cerrar un sprint
    """
    model = Sprint
    form_class = SprintCambiarEstadoForm
    context_object_name = 'sprint'
    template_name = 'change_form.html'
    pk_url_kwarg = 'sprint_id'
    permission_required = 'proyecto.administrar_sprint'

    def get(self, request, *args, **kwargs):
        try:
            id = self.kwargs['sprint_id']
            sprint = Sprint.objects.get(pk = id)
            if not sprint.es_dia_permitido():
                messages.add_message(request, messages.WARNING,
                                     'No se puede realizar esta operacion debido a que no es un dia habil de la semana!')
                return HttpResponseRedirect(reverse('proyecto_sprint_administrar',args=(sprint.proyecto.id, sprint.id)))
            return super(SprintCambiarEstadoView, self).get(request, *args, **kwargs)
        except:
            messages.add_message(request, messages.ERROR,
                                 'Ha ocurrido un error!')
            return HttpResponseRedirect(reverse('proyectos'))

    def post(self, request, *args, **kwargs):
        try:
            id = self.kwargs['sprint_id']
            sprint = Sprint.objects.get(pk = id)
            if not sprint.es_dia_permitido():
                messages.add_message(request, messages.WARNING,
                                     'No se puede realizar esta operacion debido a que no es un dia habil de la semana!')
                return HttpResponseRedirect(reverse('proyecto_sprint_administrar',args=(sprint.proyecto.id, sprint.id)))
            return super(SprintCambiarEstadoView, self).post(request, *args, **kwargs)
        except:
            messages.add_message(request, messages.ERROR,
                                 'Ha ocurrido un error!')
            return HttpResponseRedirect(reverse('proyectos'))


    def get_success_url(self):
        """
        El sitio donde se redirige al actualizar correctamente

        :return:
        """
        return reverse('proyecto_sprint_administrar', kwargs=self.kwargs)

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de edicion

        :return:
        """
        kwargs = super(SprintCambiarEstadoView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(SprintCambiarEstadoView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        context['titulo'] = 'Cerrar el Sprint'
        context['titulo_form_editar'] = '¿Desea cerrar el Sprint Nro'
        context['titulo_form_editar_nombre'] = '{}?'.format(sprint.orden)


        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden,
                                  'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
                                 {'nombre': 'Cerrar Sprint',
                                  'url': '#'}
                                 ]



        return context

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se cierra correctamente

        :param cleaned_data:
        :return:
        """
        return "Sprint Nro {} cerrado exitosamente.".format(Sprint.objects.get(pk=self.kwargs['sprint_id']).orden)

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
        """
        Se obtiene una lista de los elementos correspondientes

        :return:
        """
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
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(FlujoSprintListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        context['titulo'] = 'Escoja el Flujo'
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
                                 {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar',kwargs=self.kwargs)},
                                 {'nombre': 'Kanban', 'url':'#'}
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
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(TableroKanbanView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        try:
            flujo = Flujo.objects.get(pk=self.kwargs['flujo_id'])
            context['flujo'] = flujo
            sprint = context['sprint']
            context['user_stories_sprint'] = UserStorySprint.objects.filter(sprint=sprint, us__flujo=flujo)
        except Flujo.DoesNotExist:
            raise Http404('No existe dicho flujo')
        context['titulo'] = 'Kanban del Flujo: %s' % flujo.nombre


        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden,
                                  'url': reverse('proyecto_sprint_administrar', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id']))},
                                 {'nombre': 'Kanban', 'url': reverse('proyecto_sprint_flujos', args=(self.kwargs['proyecto_id'],self.kwargs['sprint_id']))},
                                 {'nombre': flujo.nombre, 'url':'#'}
                                 ]

        return context

@login_required
@proyecto_en_ejecucion
def mover_us_kanban(request, proyecto_id, sprint_id, flujo_id, us_id):
    """
    Vista para mover un user story a un estado. Recibe como parametro de GET, movimiento que puede tener valor 1 o -1.Que signfica avanzar o retroceder respectivamente

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
            messages.add_message(request, 'No puede realizar la accion debido a que usted no es el encargado del user story!',messages.WARNING)
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id,sprint_id,flujo_id)))
        if movimiento is None or (movimiento != 1 and movimiento != -1):
            #Si el moviemiento recibido como parametro no es valido
            messages.add_message(request,messages.WARNING,
                                 'Movimiento no permitido!'
                                 )
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))

        if user_story_sprint.fase_sprint.orden == user_story_sprint.us.flujo.cantidadFases and user_story_sprint.estado_fase_sprint=='DONE':
            #Si se encuentra en el DONE de la ultima fase y quiere moverse de estado entonces es incorrecto
            messages.add_message(request,messages.WARNING,
                                 'Movimiento no permitido!'
                                 )
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))
        if user_story_sprint.fase_sprint.orden == 1 and user_story_sprint.estado_fase_sprint=='TODO' and movimiento == -1:
            #Si se encuentra en el TO DO  de la primera fase y quiere moverse al estado anterior entonces es incorrecto
            messages.add_message(request,messages.WARNING,
                                 'Movimiento no permitido!'
                                 )
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))
        if sprint.estado != 'EN_EJECUCION':
            #Si el SPRINT NO ESTA EN EJECUCION NO SE PUEDE MOVER DE ESTADO
            messages.add_message(request,messages.WARNING,
                                 'El sprint aun no inicio!'
                                 )
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))
        if not sprint.es_dia_permitido():
            #SI NO ES UN DIA HABIL NO SE PUEDE MOVER
            messages.add_message(request, messages.WARNING,
                                 'No se puede realizar esta operacion debido a que no es un dia habil de la semana!')
            return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))

        cantidad_en_doing = user_story_sprint.asignee.userstorysprint_set.filter(estado_fase_sprint='DOING').exclude(id=user_story_sprint.id).count()
        if movimiento == 1:
            if user_story_sprint.estado_fase_sprint == 'TODO':

                if cantidad_en_doing>0:
                    #Si se quiere mover a DOING pero ya tiene uno en doing no se le permite mover
                    messages.add_message(request, messages.WARNING,
                                         'Solo tiene permitido un User Story en doing a la vez en este proyecto'
                                         )
                    return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))

                user_story_sprint.estado_fase_sprint = 'DOING'

            elif user_story_sprint.estado_fase_sprint == 'DOING':
                user_story_sprint.estado_fase_sprint = 'DONE'
                if not Actividad.objects.filter(fase=user_story_sprint.fase_sprint,usSprint=user_story_sprint, es_rechazado=False).count()>0:#SI NO HAY NINGUN ACTIVIDAD REGISTRADA EN SU FASE. NO PUEDE LLEGAR AL DONE
                    messages.add_message(request, messages.WARNING,
                                         'Al menos debe cargar una actividad para avanzar al DONE'
                                         )
                    return HttpResponseRedirect(
                        reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))

                if user_story_sprint.fase_sprint.orden == user_story_sprint.fase_sprint.flujo.cantidadFases:
                    notificar_revision(user_story_sprint)
                    messages.add_message(request, messages.INFO, 'Se notificó al Scrum Master para su '
                                         'revisión.')

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
                if cantidad_en_doing>0:
                    #Si se quiere mover a DOING pero ya tiene uno en doing no se le permite mover
                    messages.add_message(request, messages.WARNING,
                                         'Solo tiene permitido un User Story en doing a la vez en este proyecto'
                                         )
                    return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))
                user_story_sprint.estado_fase_sprint = 'DOING'
        user_story_sprint.save()

        messages.add_message(request, messages.SUCCESS,
                             'User Story {} actualizado correctamente!'.format(user_story_sprint.us.nombre)
                             )

        return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))

    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('proyecto_sprint_tablero', args=(proyecto_id, sprint_id, flujo_id)))


class SprintDeleteView(LoginRequiredMixin, PermisosPorProyectoMixin, DeleteView):
    """
        Vista Basada en Clases para la eliminacion de los Sprint
    """
    model = Sprint
    pk_url_kwarg = 'sprint_id'
    permission_required = 'proyecto.administrar_sprint'
    template_name = 'proyecto/sprint/sprint_confirm_delete.html'

    def get_success_url(self):
        """
        El sitio donde se redirige al eliminar correctamente

        :return:
        """
        return reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))

    def delete(self, request, *args, **kwargs):
        # TODO: transaction

        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        if sprint.estado == 'PLANIFICADO':
            user_sprint = UserStorySprint.objects.filter(sprint=sprint.id)
            if user_sprint.count() > 0:
                for us in user_sprint:
                    user_story=UserStory.objects.get(pk=us.us.id)
                    user_story.estadoProyecto=1
                    user_story.flujo = user_story.fase = user_story.estadoFase = None
                    user_story.save()
                    us.delete()
            messages.add_message(self.request, messages.SUCCESS, 'Sprint Eliminado')
        else:
            messages.add_message(self.request, messages.ERROR, 'No se puede eliminar este Sprint')
            return HttpResponseRedirect(reverse('proyecto_sprint_administrar',args=(sprint.proyecto.id, sprint.id)))

        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(SprintDeleteView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        context['titulo'] = 'Eliminar Sprint'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar',kwargs=self.kwargs)},
                                 {'nombre': 'Eliminar Sprint %d' % sprint.orden,
                                  'url': '#'}
                                 ]

        return context

class BurdownChartSprintView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
           Vista Basada en Clases para la visualizacion del perfil de un sprint
    """
    model = Sprint
    context_object_name = 'sprint'
    template_name = 'proyecto/sprint/burdown_chart_sprint.html'
    pk_url_kwarg = 'sprint_id'
    permission_denied_message = 'No tiene permiso para ver Proyectos.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super(BurdownChartSprintView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        context['titulo'] = 'Burdown Chart Sprint'
        datos_grafica = Actividad.objects.filter(usSprint__sprint_id=sprint.id).values('dia_sprint').annotate(
            cantidad=models.Count('dia_sprint'), total_por_dia=models.Sum('horasTrabajadas')).order_by('dia_sprint')

        x_real = [0]
        y_real = [sprint.total_horas_planificadas]
        total_dias = sprint.duracion*sprint.cant_dias_habiles
        y_ideal = []
        x_ideal = []
        total_a_trabajar = sprint.total_horas_planificadas
        acumulado = 0
        for dato in datos_grafica:
            x_real.append(dato['dia_sprint'])
            acumulado = ( acumulado + dato['total_por_dia'] )
            y_real.append(y_real[0] - acumulado)

        for dia in range(0, total_dias+1):
            x_ideal.append(dia)
            y_ideal.append(total_a_trabajar - dia*( total_a_trabajar / total_dias ))
        context['negativo'] = y_real[y_real.__len__()-1] < 0
        context['total'] = total_a_trabajar
        context['grafica'] = {'datos_en_x':x_real,'datos_en_y':y_real,'ideal_y':y_ideal,'ideal_x':x_ideal}

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
                                 {'nombre': 'Burdown Chart',
                                  'url': '#'}
                                 ]

        return context

class ReporteSprintBacklogPDF(View):
    """
    Vista que construye un pdf
    """
    def cabecera(self, pdf):
        # Utilizamos el archivo logo_django.png que está guardado en la carpeta media/imagenes
        archivo_imagen = settings.STATICFILES_DIRS[0] + '/img/logo.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)

    def get(self, request, *args, **kwargs):
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)
        # Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        # Con show page hacemos un corte de página para pasar a la siguiente
        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
        sprint = Sprint.objects.get(pk=kwargs['sprint_id'])
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        pdf.drawString(250 - 2 * len(proyecto.nombre), 790, u"" + proyecto.nombre)
        pdf.drawString(245, 770, u"Sprint"+str(sprint.orden))
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(220, 750, u"SPRINT BACKLOG")
        user_stories = UserStorySprint.objects.filter(sprint=kwargs['sprint_id']).order_by('-us__priorizacion')
        y=710
        detalles=[]
        for us in user_stories:
            detalles.append((us.us.nombre, ESTADOS_US_PROYECTO[us.us.estadoProyecto-1][1], str(us.tiempo_planificado_sprint), str(us.get_tiempo_ejecutado())))
        if not len(user_stories)>=1:
            detalles=[('Sin User Stories en el Sprint Backlog','','','')]
        cant_user_stories=len(detalles)
        y-=(20+20*cant_user_stories)
        self.tabla_us(pdf, detalles, y)
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla_us(self, pdf,detalles, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Nombre del User Story', 'Estado', 'Horas Planificadas', 'Horas Ejecutadas')
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[7 * cm, 2 * cm, 4 * cm, 4 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(35/256, 48/256, 68/256)),
                # ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 70, y)

class ReporteUSPrioridadPDF(View):
    """
    Vista que construye un pdf
    """
    def cabecera(self, pdf):
        # Utilizamos el archivo logo_django.png que está guardado en la carpeta media/imagenes
        archivo_imagen = settings.STATICFILES_DIRS[0] + '/img/logo.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)

    def get(self, request, *args, **kwargs):
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)
        # Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        # Con show page hacemos un corte de página para pasar a la siguiente
        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
        sprint = Sprint.objects.get(pk=kwargs['sprint_id'])
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        pdf.drawString(250 - 2 * len(proyecto.nombre), 790, u"" + proyecto.nombre)
        pdf.drawString(245, 770, u"Sprint"+str(sprint.orden))
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(220, 750, u"US PRIORIDAD")
        user_stories = UserStorySprint.objects.filter(sprint=kwargs['sprint_id']).exclude(us__estadoProyecto=5).order_by('-us__priorizacion')
        y=710
        detalles=[]
        for us in user_stories:
            es = 'No'
            if us.us.prioridad_suprema>0:
                es = 'Si'
            detalles.append((us.us.nombre, ESTADOS_US_PROYECTO[us.us.estadoProyecto-1][1], str(us.get_tiempo_ejecutado()),str(us.asignee.miembro.user.first_name)+" "+str(us.asignee.miembro.user.last_name),es))
        if not len(detalles)>=1:
            detalles=[('Sin User Stories que mostrar','','','','')]
        cant_user_stories=len(detalles)
        y-=(20+20*cant_user_stories)
        self.tabla_us(pdf, detalles, y)
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla_us(self, pdf,detalles, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Nombre del User Story', 'Estado','Horas Ejecutadas','Encargado','Es del sprint anterior?')
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[7 * cm, 2 * cm, 4 * cm, 4 * cm, 4 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (4, 0), colors.white),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(35/256, 48/256, 68/256)),
                # ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 10, y)
