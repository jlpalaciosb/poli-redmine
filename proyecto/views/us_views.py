from django.http import HttpResponseForbidden, Http404
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from proyecto.forms import USForm
from proyecto.mixins import PermisosPorProyectoMixin, PermisosEsMiembroMixin
from proyecto.models import MiembroProyecto, Proyecto, UserStory


class USCreateView(SuccessMessageMixin, PermisosPorProyectoMixin, LoginRequiredMixin, CreateView):
    """
    Vista para crear un US para el proyecto
    """
    model = UserStory
    template_name = "change_form.html"
    form_class = USForm
    permission_required = 'proyecto.add_us'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "US creado exitosamente"

    def get_success_url(self):
        return reverse('proyecto_us_list', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': reverse('proyecto_us_list', kwargs=self.kwargs),
            'proyecto_id': self.kwargs['proyecto_id'],
            'creando': True,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])

        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear US'
        context['titulo_form_crear'] = 'Insertar Datos del US'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
            {'nombre': 'User Stories', 'url': reverse('proyecto_us_list', kwargs=self.kwargs)},
            {'nombre': 'Crear US', 'url': '#'}
        ]

        return context


class USListView(PermisosEsMiembroMixin, LoginRequiredMixin, TemplateView):
    """
    Vista para ver el product backlog del proyecto
    """
    template_name = 'change_list.html'

    def get_context_data(self, **kwargs):
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])

        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Product Backlog'
        context['crear_button'] = self.request.user.has_perm('proyecto.add_us', p)
        context['crear_url'] = reverse('proyecto_us_crear', kwargs=self.kwargs)
        context['crear_button_text'] = 'Crear US'

        # datatables
        context['nombres_columnas'] = ['id', 'Nombre', 'Priorización']
        context['order'] = [2, "desc"]
        ver_kwargs = self.kwargs.copy()
        ver_kwargs['us_id'] = 7836271  # pasamos inicialmente un id aleatorio
        context['datatable_row_link'] = reverse('proyecto_us_ver', kwargs=ver_kwargs)
        context['list_json'] = reverse('proyecto_us_list_json', kwargs=kwargs)
        context['user_story'] = True

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', kwargs=kwargs)},
            {'nombre': 'User Stories', 'url': '#'},
        ]

        return context


class USListJsonView(PermisosEsMiembroMixin, LoginRequiredMixin, BaseDatatableView):
    """
    Vista que retorna en json la lista de user stories del product backlog
    """
    model = MiembroProyecto
    columns = ['id', 'nombre', 'priorizacion']
    order_columns = ['id', 'nombre', 'priorizacion']
    max_display_length = 100

    def get_initial_queryset(self):
        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        return p.userstory_set.all()

    #def filter_queryset(self, qs):
        #search = self.request.GET.get('search[value]', '')
        #qs_params = Q(user__username__icontains=search) | Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search)
        #return qs.filter(qs)

    #def ordering(self, qs):
        #return qs.order_by('user__username')


class USPerfilView(PermisosEsMiembroMixin, LoginRequiredMixin, DetailView):
    """
    Vista para el perfil de un miembro de un proyecto. Cualquier usuario que sea miembro del proyecto
    tiene acceso a esta vista
    """
    model = UserStory
    context_object_name = 'us'
    template_name = 'proyecto/us/us_perfil.html'
    pk_url_kwarg = 'us_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        us = context['object']

        context['titulo'] = 'Ver US'

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', args=(p.id,))},
            {'nombre': 'User Stories', 'url': reverse('proyecto_us_list', args=(p.id,))},
            {'nombre': us.nombre, 'url': '#'},
        ]

        context['puedeEditar'] = self.request.user.has_perm('proyecto.change_us', p)

        return context


class USUpdateView(SuccessMessageMixin, PermisosPorProyectoMixin, LoginRequiredMixin, UpdateView):
    """
    Vista que permite modificar los roles de un miembro de proyecto
    """
    model = UserStory
    form_class = USForm
    template_name = 'change_form.html'
    pk_url_kwarg = 'us_id'
    permission_required = 'proyecto.change_us'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "US editado exitosamente"

    def get_success_url(self):
        pid = self.kwargs['proyecto_id']
        mid = self.kwargs['us_id']
        return reverse('proyecto_us_ver', args=(pid, mid))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
            'proyecto_id': self.kwargs['proyecto_id'],
            'creando': False,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        p = Proyecto.objects.get(pk=self.kwargs['proyecto_id'])
        us = context['object']

        context['titulo'] = 'Editar Datos del US'
        context['titulo_form_editar'] = 'US'
        context['titulo_form_editar_nombre'] = us.nombre

        # Breadcrumbs
        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': p.nombre, 'url': reverse('perfil_proyecto', args=(p.id,))},
            {'nombre': 'User Stories', 'url': reverse('proyecto_us_list', args=(p.id,))},
            {'nombre': us.nombre, 'url': reverse('proyecto_us_ver', args=(p.id, us.id))},
            {'nombre': 'Editar Roles', 'url': '#'}
        ]

        return context


delete_decorators = [login_required, require_http_methods(['GET', 'POST'])]
@method_decorator(delete_decorators, name='dispatch')
class MiembroProyectoDeleteView(PermisosPorProyectoMixin, DeleteView):
    """
    Vista para excluir a un miembro del proyecto. Condiciones:
    * El miembro a excluir no debe tener el rol de 'Scrum Master'
    * El miembro a excluir no debe pertenecer a ningún sprint
    * El miembro a excluir no debe ser el mismo usuario logueado
    """
    model = MiembroProyecto
    pk_url_kwarg = 'miembro_id'
    context_object_name = 'miembro'
    permission_required = 'proyecto.delete_miembroproyecto'
    template_name = 'proyecto/miembro/miembro_confirm_delete.html'
    proyecto = None  # proyecto en cuestion
    miembro = None  # miembro en cuestion

    def dispatch(self, *args, **kwargs):
        try:
            self.proyecto = Proyecto.objects.get(pk=kwargs['proyecto_id'])
            self.miembro = MiembroProyecto.objects.get(pk=kwargs['miembro_id'])
        except (Proyecto.DoesNotExist, MiembroProyecto.DoesNotExist):
            raise Http404('no existe proyecto o miembro con el id recibido en la url')
        return super(MiembroProyectoDeleteView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo'] = 'Excluir Miembro'

        context['breadcrumb'] = [
            {'nombre': 'Inicio', 'url': '/'},
            {'nombre': 'Proyectos', 'url': reverse('proyectos')},
            {'nombre': self.proyecto.nombre, 'url': reverse('perfil_proyecto', args=(self.proyecto.id,))},
            {'nombre': 'Miembros', 'url': reverse('proyecto_miembro_list', args=(self.proyecto.id,))},
            {'nombre': self.miembro.user.username,
             'url': reverse('proyecto_miembro_perfil', args=(self.proyecto.id, self.miembro.id))},
            {'nombre': 'Excluir del Proyecto', 'url': '#'}
        ]

        eliminable = self.eliminable()
        if eliminable == 'Yes':
            context['eliminable'] = True
        else:
            context['eliminable'] = False
            context['motivo'] = eliminable

        return context

    def delete(self, request, *args, **kwargs):
        if self.eliminable() != 'Yes':
            return HttpResponseForbidden()
        return super().delete(request, *args, **kwargs)

    def eliminable(self):
        if self.miembro.roles.filter(nombre='Scrum Master').count() == 1:
            return 'es Scrum Master'
        if self.miembro.miembrosprint_set.all().count() > 0:
            return 'es miembro de al menos un sprint'
        if self.miembro.user == self.request.user:
            return ('es usted mismo (si quiere salir del proyecto solicítelo a algún miembro '
                    'que tenga el permiso de excluir miembros)')
        return 'Yes'

    def get_success_url(self):
        return reverse('proyecto_miembro_list', args=(self.proyecto.id,))
