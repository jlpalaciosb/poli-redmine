from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoSoloSePuedeVerMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, DeleteView
from proyecto.models import Sprint, Proyecto, ESTADOS_SPRINT, MiembroSprint, UserStorySprint
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from guardian.shortcuts import  get_perms
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from guardian.decorators import permission_required
from proyecto.forms import MiembroSprintForm

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

@permission_required('proyecto.administrar_sprint',(Proyecto, 'id', 'proyecto_id'), return_403=True)
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
        messages.add_message(request, messages.ERROR, 'Ya hay un sprint en planificacion!')
        return HttpResponseRedirect(reverse('proyecto_sprint_list', args=proyecto_id))
    try:
        sprint = Sprint.objects.create(proyecto=proyecto, duracion=proyecto.duracionSprint, estado='PLANIFICADO', orden=orden+1)
        messages.add_message(request, messages.SUCCESS, 'Se creo el sprint Nro '+str(orden+1))
        return HttpResponseRedirect(reverse('proyecto_sprint_list', args=proyecto_id))
    except:
        messages.add_message(request, messages.ERROR, 'Ha ocurrido un erro!')
        return HttpResponseRedirect(reverse('proyecto_sprint_list', args=proyecto_id))

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

class MiembroSprintListView(LoginRequiredMixin, PermisosEsMiembroMixin, TemplateView):
    """
    Vista para listar miembros de un sprint del proyecto
    """
    template_name = 'change_list.html'
    permission_denied_message = 'No tiene permiso para ver este proyecto.'


    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(MiembroSprintListView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
        context['titulo'] = 'Lista de Miembros de Sprints de '+ proyecto.nombre
        context['crear_button'] = 'administrar_sprint' in get_perms(self.request.user, proyecto)
        # TODO: Cambiar a agregar miembro sprint
        context['crear_url'] = reverse('proyecto_sprint_miembros_agregar', kwargs=self.kwargs)
        context['crear_button_text'] = 'Agregar miembro'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre','Horas Asignadas']
        context['order'] = [1, "des"]
        #TODO: Cambiar a ver miembro de sprint
        context['datatable_row_link'] = reverse('proyecto_sprint_administrar', args=(self.kwargs['proyecto_id'],99999))  # pasamos inicialmente el id 1
        # TODO: Cambiar a json de miembro sprint
        context['list_json'] = reverse('proyecto_sprint_miembros_json', kwargs=self.kwargs)

        context['roles']=True
        #Breadcrumbs
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                                {'nombre':'Proyectos', 'url': reverse('proyectos')},
                                {'nombre': proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                {'nombre': 'Sprints',
                                'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                {'nombre': 'Administrar Sprint', 'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
                                 {'nombre': 'Miembros Sprint', 'url': '#'}
                   ]



        return context

class MiembroSprintListJson(LoginRequiredMixin, PermisosEsMiembroMixin, BaseDatatableView):
    """
    Vista para devolver todos los miembros de un sprint del proyecto en formato JSON
    """
    model = MiembroSprint
    columns = ['id', 'miembro.user','horasAsignadas']
    order_columns = ['id', 'miembro.user','horasAsignadas']
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

class MiembroSprintCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, SuccessMessageMixin, CreateView):
    """
    Vista para creacion de un rol de proyecto. Se crean roles que no sean por defecto
    """
    model = MiembroSprint
    template_name = "change_form.html"
    form_class = MiembroSprintForm
    permission_required = 'proyecto.administrar_sprint'
    permission_denied_message = 'No tiene permiso para administrar sprint.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Miembro de Sprint agregado exitosamente."

    def get_success_url(self):
        return reverse('proyecto_sprint_miembros',kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(MiembroSprintCreateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_sprint_miembros',kwargs=self.kwargs),
            'proyecto_id': self.kwargs['proyecto_id'],
            'sprint_id': self.kwargs['sprint_id'],
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MiembroSprintCreateView, self).get_context_data(**kwargs)
        proyecto = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        context['titulo'] = 'Miembros de Sprint'
        context['titulo_form_crear'] = 'Agregar Miembro al sprint'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': proyecto.nombre,
                                  'url': reverse('perfil_proyecto', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Sprints',
                                  'url': reverse('proyecto_sprint_list', args=(self.kwargs['proyecto_id'],))},
                                 {'nombre': 'Administrar Sprint',
                                  'url': reverse('proyecto_sprint_administrar', kwargs=self.kwargs)},
                                 {'nombre': 'Miembros Sprint', 'url': reverse('proyecto_sprint_miembros',kwargs=self.kwargs)},
                                 {'nombre': 'Crear', 'url':'#'}
                                 ]

        return context


