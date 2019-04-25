from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin, ProyectoSoloSePuedeVerMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, DeleteView
from proyecto.models import Sprint, Proyecto, MiembroSprint
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from guardian.shortcuts import  get_perms
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib.messages.views import SuccessMessageMixin
from proyecto.forms import MiembroSprintForm

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
