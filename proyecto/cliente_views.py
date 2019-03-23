from django.http import HttpResponseForbidden
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from proyecto.forms import ClienteForm
from proyecto.models import Cliente


class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'proyecto/cliente/cliente_list.html'
    permission_required = 'proyecto.view_cliente'
    permission_denied_message = 'No tiene permiso para ver la lista de clientes.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ClienteListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Clientes'
        context['crear_url'] = reverse('crear_cliente')
        context['crear_button_text'] = 'Nuevo Cliente'

        # datatable
        context['nombres_columnas'] = ['id', 'RUC', 'Nombre', 'Dirección', 'Teléfono']
        context['order'] = [1, 'asc']
        context['datatable_row_link'] = reverse('perfil_cliente', args=(1,))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('cliente_list_json')

        # breadcrumb
        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'}, {'nombre':'Clientes', 'url': '#'},]

        return context


class ClienteListJson(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    model = Cliente
    columns = ['id', 'ruc', 'nombre', 'direccion', 'telefono']
    order_columns = ['id', 'ruc', 'nombre', 'direccion', 'telefono']
    max_display_length = 100
    permission_required = 'proyecto.view_cliente'
    permission_denied_message = 'No tiene permiso para ver la lista de clientes.'


class ClientePerfilView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Cliente
    context_object_name = 'cliente'
    template_name = 'proyecto/cliente/cliente_perfil.html'
    pk_url_kwarg = 'cliente_id'
    permission_required = 'proyecto.view_cliente'
    permission_denied_message = 'No tiene permiso para ver este cliente.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ClientePerfilView, self).get_context_data(**kwargs)
        context['titulo'] = 'Perfil de Cliente'

        # breadcrumb
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Clientes', 'url': reverse('clientes')},
                                 {'nombre': context['cliente'].nombre,'url': '#'}
                                ]

        return context


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Cliente
    template_name = "proyecto/cliente/cliente_form.html"
    form_class = ClienteForm
    permission_required = 'proyecto.add_cliente'
    permission_denied_message = 'No tiene permiso para registrar nuevos clientes.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Cliente '{}' registrado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('clientes')

    def get_form_kwargs(self):
        kwargs = super(ClienteCreateView, self).get_form_kwargs()
        kwargs.update({'success_url': reverse('clientes'),})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ClienteCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Registrar Cliente'
        context['titulo_form_crear'] = 'Insertar Datos del Nuevo Cliente'

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Clientes', 'url': reverse('clientes')},
                                 {'nombre': 'Nuevo Cliente', 'url': '#'}
                                ]

        return context


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    context_object_name = 'proyecto'
    template_name = 'proyecto/cliente/cliente_form.html'
    pk_url_kwarg = 'proyecto_id'
    permission_required = 'proyecto.change_proyecto'
    permission_denied_message = 'No tiene permiso para Editar Proyectos.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Proyecto '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('perfil_proyecto', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(ClienteUpdateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ClienteUpdateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Proyecto'
        context['titulo_form_editar'] = 'Datos del Proyecto'
        context['titulo_form_editar_nombre'] = context[ClienteUpdateView.context_object_name].nombre

        # Breadcrumbs
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Proyectos', 'url': reverse('proyectos')},
                                 {'nombre': context['proyecto'].nombre, 'url': reverse('perfil_proyecto', kwargs=self.kwargs)},
                                 {'nombre': 'Editar', 'url': '#'},
                                 ]

        return context

    def form_valid(self, form):
        proyecto = form.save(commit=False)
        if not form.instance.pk:
            proyecto.usuario_creador_id = self.request.user.id
            proyecto.usuario_modificador_id = self.request.user.id
        else:
            proyecto.usuario_modificador_id = self.request.user.id

        return super().form_valid(form)
