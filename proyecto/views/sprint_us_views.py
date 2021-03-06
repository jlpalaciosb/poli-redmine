from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, DeleteView, FormView
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from guardian.mixins import LoginRequiredMixin

from ProyectoIS2_9.utils import notificar_asignacion, notificar_aceptacion, notificar_rechazo
from proyecto.forms import UserStorySprintCrearForm, UserStorySprintEditarForm, RechazarUSFormViejo, RechazarUSForm
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoEnEjecucionMixin
from proyecto.models import Sprint, Proyecto, UserStorySprint, Actividad, MiembroProyecto
from guardian.decorators import permission_required
from django.contrib.auth.decorators import login_required
from proyecto.decorators import proyecto_en_ejecucion


class UserStorySprintCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, CreateView):
    """
    Vista para agregar un user story a un sprint
    """
    model = UserStorySprint
    template_name = "proyecto/usp/usp_create.html"
    form_class = UserStorySprintCrearForm
    permission_required = 'proyecto.administrar_sprint'

    def get_success_url(self):
        """
        El sitio donde se redirige al crear correctamente

        :return:
        """
        return reverse('sprint_us_list', kwargs=self.kwargs)

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de creacion

        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
            'sprint_id': self.kwargs['sprint_id'],
        })
        return kwargs

    def form_valid(self, form):
        """
        Se cambia las fases y estados del user story sprint al valor inicial o en caso de ser uno que continua al valor dejado en el sprint anterior

        :param form:
        :return:
        """
        # TODO : transaction

        # establecer estado del us seleccionado y su flujo
        us = form.cleaned_data['us']
        flujo = form.cleaned_data['flujo']

        if us.flujo is None:
            us.flujo = flujo
            us.fase = flujo.fase_set.get(orden=1)
            us.estadoFase = 'TODO'
            #se coloca la fase y el estado al user story sprint
            form.instance.fase_sprint = us.fase
            form.instance.estado_fase_sprint = us.estadoFase
        if us.estadoProyecto == 3 :#SI el estado del US a asignar es NO TERMINADO entonces se copia las fases y estados al User Story Sprint actual
            form.instance.fase_sprint = us.fase
            form.instance.estado_fase_sprint = us.estadoFase
            if us.estadoFase == 'DOING':#SI SE QUEDO EN EL DOING ENTONCES VUELVE AL TO DO DE SU FASE ACTUAL
                form.instance.estado_fase_sprint = 'TODO'
            # form.instance.prioridad_suprema = True
        us.estadoProyecto = 2
        us.save()

        # calcular cantidad de horas disponibles en el sprint (recordar que sprint tiene un atributo llamado capacidad)
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        suma = 0 # cantidad de horas de trabajo por hacer
        for usp in UserStorySprint.objects.filter(sprint=sprint):
            restante = usp.us.tiempoPlanificado - usp.us.tiempoEjecutado
            suma += restante
        suma += us.tiempoPlanificado - us.tiempoEjecutado # sumar trabajo restante del US que se está agregando
        disponible = sprint.capacidad - suma
        if disponible > 0: messages.add_message(self.request, messages.INFO, 'Quedan ' + str(disponible) + ' horas disponibles en el sprint')
        else: messages.add_message(self.request, messages.WARNING, 'Capacidad del sprint superada por ' + str(-disponible) + ' horas')

        ret = super().form_valid(form)

        if form.instance.asignee.horas_ocupadas_planificadas() > form.instance.asignee.capacidad():#SI SE EXCEDE LA CAPACIDAD DEL MIEMBRO
            messages.add_message( self.request, messages.WARNING, 'Se ha excedido la capacidad planificada del miembro ' + form.instance.asignee.__str__())

        notificar_asignacion(form.instance)
        messages.add_message(self.request, messages.INFO, 'Se notificó al asignado')
        return ret

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Agregar US al Sprint'
        context['titulo_form_crear'] = 'Datos'

        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
            {'nombre': 'Sprint Backlog', 'url': self.get_success_url()},
            {'nombre': 'Agregar US', 'url':'#'}
        ]

        return context


class UserStorySprintListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para ver el sprint backlog
    """
    template_name = 'proyecto/usp/usp_list.html'
    filtro = '*'

    def dispatch(self, request, *args, **kwargs):
        self.filtro = request.GET.get('filtro', '*')
        self.filtro = '*' if self.filtro not in ['1', '2', '3'] else self.filtro
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])

        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Sprint Backlog'
        context['crear_button'] = self.request.user.has_perm('proyecto.administrar_sprint', proyecto) and sprint.estado == 'PLANIFICADO'
        context['crear_url'] = reverse('sprint_us_agregar', kwargs=self.kwargs)
        context['crear_button_text'] = 'Agregar US'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre', 'Priorización', 'Encargado']
        context['order'] = [2, "desc"]
        context['datatable_row_link'] = reverse('sprint_us_ver', args=(proyecto.id, sprint.id, 7483900))
        context['list_json'] = reverse('sprint_us_list_json', kwargs=kwargs) + '?filtro=' + self.filtro
        context['usp'] = True

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
            {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
            {'nombre': 'Sprint Backlog', 'url': '#'},
        ]

        context['selected'] = self.filtro

        return context


class UserStorySprintListJsonView(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista que retorna en json la lista de user stories del sprint backlog
    """
    model = UserStorySprint
    columns = ['id', 'us.nombre', 'us.priorizacion', 'asignee']
    order_columns = ['id', 'us.nombre', 'us.priorizacion', 'asignee']
    max_display_length = 100

    def get_initial_queryset(self):
        """
        Se obtiene una lista de los elementos correspondientes

        :return:
        """
        filtro = self.request.GET.get('filtro', '*')
        qs = UserStorySprint.objects.filter(sprint__id=self.kwargs['sprint_id'])
        if filtro == '3': # terminado
            qs = qs.filter(us__estadoProyecto=5)
        elif filtro == '2': # en revisión
            qs = qs.filter(us__estadoProyecto=6)
        elif filtro == '1': # en progreso
            qs = qs.exclude(us__estadoProyecto__in=[5, 6])
        return qs

    def render_column(self, usp, column):
        """

        :type usp: UserStorySprint
        """
        if column == 'us.nombre' and usp.sprint.estado != 'CERRADO':
            suffix = '¡NT!' if usp.us.prioridad_suprema else ''
            return usp.us.nombre + suffix
        elif column == 'us.priorizacion': return "{0:.2f}".format(usp.us.get_priorizacion())
        elif column == 'asignee': return usp.asignee.miembro.user.get_full_name()
        else: return super().render_column(usp, column)

    def filter_queryset(self, qs):
        search = self._querydict.get('search[value]', '')
        return qs.filter(us__nombre__icontains=search)


class UserStorySprintPerfilView(LoginRequiredMixin, PermisosEsMiembroMixin, DetailView):
    """
    Vista para ver los datos básicos de un User Story a nivel de sprint
    """
    model = UserStorySprint
    context_object_name = 'usp'
    template_name = 'proyecto/usp/usp_perfil.html'
    pk_url_kwarg = 'usp_id'

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)

        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        usp = context['object']

        context['titulo'] = 'User Story (en sprint)'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(proyecto.id,))},
            {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(proyecto.id, sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(proyecto.id, sprint.id))},
            {'nombre': usp.us.nombre, 'url': '#'},
        ]

        context['puedeEditar'] = self.request.user.has_perm('proyecto.administrar_sprint', proyecto)

        return context


class UserStorySprintEditarView(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, UpdateView):
    """
    Vista que permite modificar un User Story a nivel de sprint (hasta ahora solo se permite cambiar el asignee)
    """
    model = UserStorySprint
    form_class = UserStorySprintEditarForm
    template_name = 'change_form.html'
    pk_url_kwarg = 'usp_id'
    permission_required = 'proyecto.administrar_sprint'

    def dispatch(self, request, *args, **kwargs):
        if not self.cambiable():
            return HttpResponseForbidden()
        else:
            return super().dispatch(request, *args, **kwargs)

    def cambiable(self):
        return self.get_object().sprint.estado != 'CERRADO'

    def get_success_message(self, cleaned_data):
        """
        :return: el mensaje que aparece cuando se crea correctamente
        """
        return "Se editó exitosamente el user story en sprint"

    def get_success_url(self):
        """
        El sitio donde se redirige al cargar correctamente

        :return:
        """
        pid = self.kwargs['proyecto_id']
        sid = self.kwargs['sprint_id']
        uid = self.kwargs['usp_id']
        return reverse('sprint_us_ver', args=(pid, sid, uid))

    def get_form_kwargs(self):
        """
        Las variables que maneja el form de creacion

        :return:
        """
        kwargs = super().get_form_kwargs()
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
        context = super().get_context_data(**kwargs)

        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        usp = context['object']

        context['titulo'] = 'Editar US en Sprint'
        context['titulo_form_editar'] = 'User Story'
        context['titulo_form_editar_nombre'] = usp.us.nombre

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(proyecto.id,))},
            {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(proyecto.id, sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(proyecto.id, sprint.id))},
            {'nombre': usp.us.nombre, 'url': reverse('sprint_us_ver', args=(proyecto.id, sprint.id, usp.id))},
            {'nombre': 'Cambiar Encargado', 'url': '#'},
        ]

        return context


class UserStorySprintDeleteView(LoginRequiredMixin, PermisosPorProyectoMixin, DeleteView):
    model = UserStorySprint
    pk_url_kwarg = 'usp_id'
    permission_required = 'proyecto.administrar_sprint'

    def get_success_url(self):
        """
        El sitio donde se redirige al eliminar correctamente

        :return:
        """
        return reverse('sprint_us_list', args=(self.kwargs['proyecto_id'], self.kwargs['sprint_id']))

    def delete(self, request, *args, **kwargs):
        """
        Para eliminar se comprueba cual sera su estado de proyecto pudiendo ser PENDIENTE o NO TERMINADO

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # TODO: transaction

        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        if sprint.estado != 'PLANIFICADO':
            return HttpResponseForbidden()

        us = self.get_object().us
        if us.userstorysprint_set.count() > 1: # el US fue agregado a un sprint anterior
            us.estadoProyecto = 3 # no terminado
        else:
            us.estadoProyecto = 1 # pendiente
            us.flujo = us.fase = us.estadoFase = None
        us.save()

        messages.add_message(self.request, messages.SUCCESS, 'User Story quitado del sprint')
        return super().delete(request, *args, **kwargs)


@login_required
@permission_required('proyecto.administrar_sprint',(Proyecto, 'id', 'proyecto_id'), return_403=True)
@proyecto_en_ejecucion
def aprobar_user_story(request, proyecto_id, sprint_id, usp_id):
    """
    Vista para culminar definitavemente un user story. Es decir colocarle el estado terminado

    :param request:
    :param proyecto_id: el id del proyecto
    :param sprint_id: el id del sprint
    :param usp_id: el id del user story sprint
    :return:
    """
    try:
        sprint = Sprint.objects.get(pk=sprint_id, proyecto_id=proyecto_id)
        if sprint.estado != 'EN_EJECUCION':
            messages.add_message(request, messages.WARNING, 'El Sprint debe estar en ejecucion')
            return HttpResponseRedirect(reverse('sprint_us_ver', args=(proyecto_id, sprint_id,usp_id)))
        user_story_sprint = UserStorySprint.objects.get(pk=usp_id, sprint_id=sprint_id, sprint__proyecto_id=proyecto_id)
        us = user_story_sprint.us
        if not (us.estadoFase == 'DONE' and us.fase.orden == us.flujo.cantidadFases):
            messages.add_message(request, messages.WARNING, 'El User Story debe estar en el DONE de su ultima fase')
            return HttpResponseRedirect(reverse('sprint_us_ver',args=(proyecto_id,sprint_id,usp_id)))
        if us.estadoProyecto != 6:
            messages.add_message(request, messages.WARNING, 'El User Story debe estar en revision')
            return HttpResponseRedirect(reverse('sprint_us_ver',args=(proyecto_id,sprint_id,usp_id)))
        us.estadoProyecto = 5 #Se coloca al user story en el estado terminado
        us.prioridad_suprema = 0
        us.save()
        messages.add_message(request, messages.SUCCESS, 'El User Story {} ha culminado exitosamente'.format(us.nombre))
        notificar_aceptacion(user_story_sprint)
        messages.add_message(request, messages.INFO, 'Se notificó al encargado')
        return HttpResponseRedirect(reverse('sprint_us_ver',args=(proyecto_id,sprint_id,usp_id)))
    except UserStorySprint.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'El User Story solicitido no existe')
        return HttpResponseRedirect(reverse('sprint_us_list',args=(proyecto_id, sprint_id)))
    except Sprint.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'El Sprint solicitido no existe')
        return HttpResponseRedirect(reverse('perfil_proyecto', args=(proyecto_id,)))
    except:
        messages.add_message(request, messages.ERROR, 'Ha ocurrido un error!')
        return HttpResponseRedirect(reverse('sprint_us_list', args=(proyecto_id, sprint_id)))


class UserStorySprintRechazarViewViejo(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin, ProyectoEnEjecucionMixin, UpdateView):
    """
    Vista que permite a un scrum master rechazar un user story que este en revision.
    Se le manda al TO DO de alguna fase
    """
    model = UserStorySprint
    form_class = RechazarUSFormViejo
    template_name = 'change_form.html'
    pk_url_kwarg = 'usp_id'
    permission_required = 'proyecto.administrar_sprint'

    def get_success_message(self, cleaned_data):
        """
        El mensaje que aparece cuando se rechaza correctamente

        :param cleaned_data:
        :return:
        """
        return "Se rechazo el user story correctamente"

    def get_success_url(self):
        """
        El sitio donde se redirige al rechazar correctamente

        :return:
        """
        pid = self.kwargs['proyecto_id']
        sid = self.kwargs['sprint_id']
        uid = self.kwargs['usp_id']
        return reverse('sprint_us_ver', args=(pid, sid, uid))

    def get_form_kwargs(self):
        """
        Las variables que maneja el form

        :return:
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url()
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Las variables de contexto del template

        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)

        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        sprint = Sprint.objects.get(pk=self.kwargs['sprint_id'])
        usp = context['object']

        context['titulo'] = 'Rechazar culminacion del User Story'
        context['titulo_form_editar'] = 'US'
        context['titulo_form_editar_nombre'] = usp.us.nombre

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(proyecto.id,))},
            {'nombre': 'Sprint %d' % sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(proyecto.id, sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(proyecto.id, sprint.id))},
            {'nombre': usp.us.nombre, 'url': reverse('sprint_us_ver', args=(proyecto.id, sprint.id, usp.id))},
            {'nombre': 'Rechazar User Story', 'url': '#'},
        ]

        return context

    def get(self, request, *args, **kwargs):
        response = self.es_valido(request)
        if response is None:
            return super(UserStorySprintRechazarViewViejo, self).get(request, args, kwargs)
        return response


    def post(self, request, *args, **kwargs):
        response = self.es_valido(request)
        if response is None:
            return super(UserStorySprintRechazarViewViejo, self).post(request, args, kwargs)
        return response


    def es_valido(self, request):
        """
        Controla si se puede acceder a esta vista

        **Condiciones**
        - El Sprint debe estar en ejecucion
        - El User Story debe estar en el DONE de su ultima fase
        - El User Story debe estar en revision

        :param request:
        :return:
        """
        proyecto_id = self.kwargs['proyecto_id']
        sprint_id = self.kwargs['sprint_id']
        usp_id = self.kwargs['usp_id']
        try:
            sprint = Sprint.objects.get(pk=sprint_id, proyecto_id=proyecto_id)
            if sprint.estado != 'EN_EJECUCION':
                messages.add_message(request, messages.WARNING, 'El Sprint debe estar en ejecucion')
                return HttpResponseRedirect(reverse('sprint_us_ver', args=(proyecto_id, sprint_id, usp_id)))
            user_story_sprint = UserStorySprint.objects.get(pk=usp_id, sprint_id=sprint_id,
                                                            sprint__proyecto_id=proyecto_id)
            us = user_story_sprint.us
            if not (us.estadoFase == 'DONE' and us.fase.orden == us.flujo.cantidadFases):
                messages.add_message(request, messages.WARNING, 'El User Story debe estar en el DONE de su ultima fase')
                return HttpResponseRedirect(reverse('sprint_us_ver', args=(proyecto_id, sprint_id, usp_id)))
            if us.estadoProyecto != 6:
                messages.add_message(request, messages.WARNING, 'El User Story debe estar en revision')
                return HttpResponseRedirect(reverse('sprint_us_ver', args=(proyecto_id, sprint_id, usp_id)))
            return None
        except UserStorySprint.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'El User Story solicitido no existe')
            return HttpResponseRedirect(reverse('sprint_us_list', args=(proyecto_id, sprint_id)))
        except Sprint.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'El Sprint solicitido no existe')
            return HttpResponseRedirect(reverse('perfil_proyecto', args=(proyecto_id,)))
        except:
            messages.add_message(request, messages.ERROR, 'Ha ocurrido un error!')
            return HttpResponseRedirect(reverse('sprint_us_list', args=(proyecto_id, sprint_id)))

    def form_valid(self, form):
        """
        Se cambia nuevamente el estado del user story a EN SPRINT

        :param form:
        :return:
        """
        response = super(UserStorySprintRechazarViewViejo, self).form_valid(form)
        form.instance.us.estadoProyecto = 2
        form.instance.us.save()
        notificar_rechazo(form.instance)
        messages.add_message(self.request, messages.INFO, 'Se notificó al encargado')
        return response


class UserStorySprintRechazarView(SuccessMessageMixin, LoginRequiredMixin, PermisosPorProyectoMixin,
        ProyectoEnEjecucionMixin, FormView):
    """
    Vista que permite a un scrum master rechazar un user story que esté en revisión. Se le manda
    al UserStorySprint al TO DO de alguna fase. Se crea una actividad para la nota de rechazo.
    """
    form_class = RechazarUSForm
    template_name = 'change_form.html'
    permission_required = 'proyecto.administrar_sprint'
    proyecto = None # el proyecto en cuestión (se inicializa en el método es_valido)
    sprint = None # el sprint en cuestión (se inicializa en el método es_valido)
    usp = None # el userstorysprint en cuestión (se inicializa en el método es_valido)

    def dispatch(self, request, *args, **kwargs):
        response = self.es_valido(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs) if response is None else response

    def get_success_message(self, cleaned_data):
        """
        :return el mensaje que aparece cuando se rechaza correctamente
        """
        return "Se rechazó el user story correctamente"

    def get_success_url(self):
        """
        :return la url (string) de la página donde se redirige cuando se rechaza correctamente
        """
        return reverse('sprint_us_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id))

    def get_form_kwargs(self):
        """
        :return las variables que maneja el form
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'usp': self.usp
        })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        :return las variables de contexto del template
        """
        context = super().get_context_data(**kwargs)

        context['titulo'] = 'Rechazar culminación del User Story'
        context['form_rechazar_us'] = True
        context['titulo_form_editar'] = 'US'
        context['titulo_form_editar_nombre'] = self.usp.us.nombre

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.proyecto.id,))},
            {'nombre': 'Sprints', 'url': reverse('proyecto_sprint_list', args=(self.proyecto.id,))},
            {'nombre': 'Sprint %d' % self.sprint.orden, 'url': reverse('proyecto_sprint_administrar', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': 'Sprint Backlog', 'url': reverse('sprint_us_list', args=(self.proyecto.id, self.sprint.id))},
            {'nombre': self.usp.us.nombre, 'url': reverse('sprint_us_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id))},
            {'nombre': 'Rechazar User Story', 'url': '#'},
        ]

        return context

    def es_valido(self, request, *args, **kwargs):
        """
        Controla si se puede acceder a esta vista. También inicializa los atributos proyecto,
        sprint y usp

        ** Condiciones **
        - El Sprint debe estar en ejecucion
        - El User Story debe estar en el DONE de su ultima fase
        - El User Story debe estar en revision

        :return la respuesta en caso de invalidez, None si es válido
        """
        proyecto_id = kwargs['proyecto_id']
        sprint_id = kwargs['sprint_id']
        usp_id = kwargs['usp_id']
        try:
            self.sprint = Sprint.objects.get(pk=sprint_id, proyecto_id=proyecto_id)
            if self.sprint.estado != 'EN_EJECUCION':
                messages.add_message(request, messages.WARNING, 'El Sprint debe estar en ejecución')
                return HttpResponseRedirect(reverse('sprint_us_ver', args=(proyecto_id, sprint_id, usp_id)))

            self.usp = UserStorySprint.objects.get(pk=usp_id, sprint_id=sprint_id, sprint__proyecto_id=proyecto_id)
            us = self.usp.us

            if not (us.estadoFase == 'DONE' and us.fase.orden == us.flujo.cantidadFases):
                messages.add_message(request, messages.WARNING, 'El User Story debe estar en el DONE de su ultima fase')
                return HttpResponseRedirect(reverse('sprint_us_ver', args=(proyecto_id, sprint_id, usp_id)))

            if us.estadoProyecto != 6:
                messages.add_message(request, messages.WARNING, 'El User Story debe estar en revision')
                return HttpResponseRedirect(reverse('sprint_us_ver', args=(proyecto_id, sprint_id, usp_id)))

            self.proyecto = self.usp.sprint.proyecto

            return None # petición válida
        except UserStorySprint.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'El User Story solicitido no existe')
            return HttpResponseRedirect(reverse('sprint_us_list', args=(proyecto_id, sprint_id)))
        except Sprint.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'El Sprint solicitido no existe')
            return HttpResponseRedirect(reverse('perfil_proyecto', args=(proyecto_id,)))
        except: # it does not matter if this clause if too broad
            messages.add_message(request, messages.ERROR, 'Ha ocurrido un error!')
            return HttpResponseRedirect(reverse('sprint_us_list', args=(proyecto_id, sprint_id)))

    def form_valid(self, form):
        """
        Se cambia nuevamente el estado del user story a EN SPRINT
        """
        response = super(UserStorySprintRechazarView, self).form_valid(form)

        # generar la actividad
        Actividad.objects.create(
            nombre='Rechazo de User Story',
            descripcion=form.cleaned_data['descripcion'],
            usSprint=self.usp,
            responsable=MiembroProyecto.objects.get(user=self.request.user, proyecto=self.proyecto),
            horasTrabajadas=0,
            fase=self.usp.fase_sprint,
            estado=self.usp.estado_fase_sprint,
            es_rechazado=True
        )

        #invalidar todas las actividades que hayan sido cargadas en las fases igual o superior a la fase seleccionada
        for act in Actividad.objects.filter(usSprint=self.usp, fase__orden__gte=form.cleaned_data['fase'].orden):
            act.es_rechazado = True
            act.save()

        # modificar el usp
        self.usp.fase_sprint = form.cleaned_data['fase']
        self.usp.estado_fase_sprint = 'TODO'
        self.usp.save()

        # modificar el us
        self.usp.us.estadoProyecto = 2 # el US estaba en revisión, ahora volverá a estar en sprint
        self.usp.us.save()

        # notificar por correo al encargado
        notificar_rechazo(self.usp)
        messages.add_message(self.request, messages.INFO, 'Se notificó al encargado')

        return response
